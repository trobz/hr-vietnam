# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _order = 'date_to desc, id desc'

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        Override function
        @param contracts: list of contract
        @return:
        - ScheduleDays depends on working schedule
        - WorkedDays depends on payslip and contract period
        - Unpaid leaves
        returns a list of dictionary which containing the input that should be
        applied for the given contract between date_from and date_to
        """

        def get_working_day(calendar, date):
            """
            @param date: given date
            @param calendar: resource.calendar recordset
            Return: working day = 1 or 0.5
            based on resource.calendar.attendance.type
            """
            weekday = date.weekday()
            date = date.strftime(DF)
            res = 0
            for att in calendar.attendance_ids:
                if int(att.dayofweek) == weekday:
                    if not ((att.date_from and date < att.date_from) or (
                            att.date_to and date > att.date_to)):
                        res += att.type == 'full' and 1 or 0.5
            return res

        res = []
        contract_obj = self.env['hr.contract']
        holiday_obj = self.env['hr.holidays']
        for contract in contracts:
            if not contract.resource_calendar_id:
                # No working schedule defined this contract
                continue
            calendar = {'name': _("Working schedule"),
                        'sequence': 0,
                        'code': 'ScheduleDays',
                        'number_of_days': 0,
                        'number_of_hours': 0,
                        'contract_id': contract.id}
            attendances = {'name': _("Working days"), 'code': 'WorkingDays',
                           'number_of_days': 0.0, 'number_of_hours': 0.0,
                           'contract_id': contract.id, }
            leaves = {
                'name': 'Unpaid leaves',
                'sequence': 2,
                'code': 'UnpaidL',
                'number_of_days': 0,
                'number_of_hours': 0,
                'contract_id': contract.id,
            }
            contract_date_start = contract.date_start
            contract_date_end = contract.date_end
            max_date_from = datetime.strptime(
                max(contract_date_start, date_from), DF)
            min_date_to = datetime.strptime(date_to, DF)
            if contract_date_end and contract_date_end <= date_to:
                min_date_to = datetime.strptime(contract_date_end, DF)
            month_start = max_date_from + relativedelta(day=1)
            month_end = min_date_to + relativedelta(months=1, day=1, days=-1)
            nb_of_days_in_month = (month_end - month_start).days + 1
            nb_of_days = (min_date_to - max_date_from).days + 1

            # Calculate ScheduledDays from 01/M to end of Month
            resource_calendar_id = contract.resource_calendar_id and \
                contract.resource_calendar_id.id or False
            for day in range(0, nb_of_days_in_month):
                date = month_start + relativedelta(days=day)
                working_hours_on_day = \
                    contract.resource_calendar_id.get_work_hours_count(
                        start_dt=date, end_dt=False,
                        resource_id=resource_calendar_id, compute_leaves=False)
                if working_hours_on_day:
                    wday = get_working_day(contract.resource_calendar_id, date)
                    calendar['number_of_days'] += min(1, wday)
                    calendar['number_of_hours'] += working_hours_on_day

            # Calculate WorkedDays from MAX(contract start, payslip start)
            #     to MIN(contract end, payslip end)
            for day in range(0, nb_of_days):
                date = max_date_from + relativedelta(days=day)
                working_hours_on_day = \
                    contract.resource_calendar_id.get_work_hours_count(
                        start_dt=date, end_dt=False,
                        resource_id=resource_calendar_id, compute_leaves=False)
                if working_hours_on_day:
                    wday = get_working_day(contract.resource_calendar_id, date)
                    attendances['number_of_days'] += min(1, wday)
                    attendances['number_of_hours'] += working_hours_on_day
            attendances.update({'name': _("Working days from %s to %s" % (
                max_date_from.strftime('%d/%m/%Y'),
                min_date_to.strftime('%d/%m/%Y')))})

            # Unpaid leaves
            leave_types = self.env['hr.holidays.status'].search(
                [('payment_type', '=', 'unpaid')])
            ldays, leave_requests = holiday_obj.compute_leave_days(
                contract.employee_id.id, leave_types.ids,
                max_date_from.strftime(DF), min_date_to.strftime(DF))
            leaves['number_of_days'] = ldays
            leaves['number_of_hours'] += ldays * 8
            # Change payslip_status is not enough to keep track which
            # leave requests paid already
            # TODO: on leave requests, add list payslip, leave days
            # auto update when approving payslip and refund payslip
            # Next payslip must only take into account the leave days that
            # NOT paid yet
            if leave_requests:
                leave_requests.write({'payslip_status': True})
            res += [attendances, calendar, leaves]
        return res

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        Override function
        The native function is incorrect in case computing
            payslip with several contracts in payslip period
        """

        res = []
        contract_obj = self.env['hr.contract']
        rule_obj = self.env['hr.salary.rule']
        structure_obj = self.env['hr.payroll.structure']
        for contract in contracts:
            structure_ids = contract.get_all_structures()
            structure_obj._ids = structure_ids
            rule_ids = structure_obj.get_all_rules()
            sorted_rule_ids = [x[0] for x in
                               sorted(rule_ids, key=lambda x: x[1])]
            for rule in rule_obj.browse(sorted_rule_ids):
                for s_input in rule.input_ids:
                    res.append({'name': s_input.name, 'code': s_input.code,
                                'contract_id': contract.id, })
        return res

    def get_contract(self, employee, date_from, date_to):
        """
        @param employee: recordset of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee
        that need to be considered for the given dates
        """
        # a contract is valid if it ends between the given dates
        if self._context.get('contract_state_condition'):
            contract_state_condition = self._context[
                'contract_state_condition']
            clause_1 = ['&', ('date_end', '<=', date_to),
                        ('date_end', '>=', date_from)]
            # OR if it starts between the given dates
            clause_2 = ['&', ('date_start', '<=', date_to),
                        ('date_start', '>=', date_from)]
            # OR if it starts before the date_from and finish
            # after the date_end (or never finish)
            clause_3 = ['&', ('date_start', '<=', date_from), '|',
                        ('date_end', '=', False), ('date_end', '>=', date_to)]
            clause_final = [('employee_id', '=', employee.id),
                            contract_state_condition, '|',
                            '|'] + clause_1 + clause_2 + clause_3
            return self.env['hr.contract'].search(clause_final).ids
        else:
            return super(HrPayslip, self).get_contract(employee, date_from,
                                                       date_to)

    @api.onchange('date_from', 'date_to', 'employee_id', 'contract_id')
    def onchange_employee(self):
        """
        # TODO: remove these changes when native odoo fixed
        Rewrite onchange_employee to fix non suitable points
        - Run onchange_employee when change date_to
        - Set NULL contract_id and structure_id if:
            - employee has no contract on payslip period
            - employee has many contracts on payslip period,
                to compute payslip based on these contracts
        """
        if not self.employee_id or not self.date_from or not self.date_to:
            return

        employee_id = self.employee_id
        date_from = self.date_from
        date_to = self.date_to

        dt_date_from = datetime.strptime(date_from, DF)
        self.name = _('Salary Slip of %s for %s') % (
            employee_id.name, dt_date_from.strftime('%B-%Y'))
        self.company_id = employee_id.company_id

        contract_ids = self.with_context(
            contract_state_condition=(
                'state', 'in', ('open', 'close'))).get_contract(
            self.employee_id, self.date_from, self.date_to)
        if len(contract_ids) == 1:
            self.contract_id = contract_ids[0]
            self.struct_id = self.contract_id.struct_id and \
                self.contract_id.struct_id.id or False
        else:
            self.contract_id = False
            self.struct_id = False

        # Get jounal from the first contract.
        contracts = self.env['hr.contract']
        if contract_ids:
            contracts = self.env['hr.contract'].browse(contract_ids)
            self.journalid = contracts[0].journal_id and contracts[
                0].journal_id.id or False

        # computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(contracts,
                                                         date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines

        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        input_lines = self.input_line_ids.browse([])
        for r in input_line_ids:
            input_lines += input_lines.new(r)
        self.input_line_ids = input_lines

    def _prepare_payslip_line(self, rule, employee_id, contract_id=False):
        """
        Prepare data for a payslip line to create a new one
        """
        res = {
            'slip_id': False,
            'name': rule.name,
            'code': rule.code,
            'sequence': rule.sequence,
            'category_id': rule.category_id.id,
            'salary_rule_id': rule.id,
            'contract_id': contract_id,
            'appears_on_payslip': rule.appears_on_payslip,
            'condition_select': rule.condition_select,
            'condition_python': rule.condition_python,
            'condition_range': rule.condition_range,
            'condition_range_min': rule.condition_range_min,
            'condition_range_max': rule.condition_range_max,
            'amount_select': rule.amount_select,
            'amount_fix': rule.amount_fix,
            'amount_python_compute': rule.amount_python_compute,
            'amount_percentage': rule.amount_percentage,
            'amount_percentage_base': rule.amount_percentage_base,
            'register_id': rule.register_id.id,
            'amount': 0,
            'employee_id': employee_id,
            'quantity': 1,
            'rate': 100,
        }
        return res

    def sumdict(self, dicts):
        """
        @param dicts: list dictionary
        @return: A new dictionary has the values that sum of values
            by the same key in the given dictionaries
        """
        result = {}
        for _dict in dicts:
            for key, value in _dict.items():
                if key not in result:
                    result[key] = 0
                result[key] = result[key] + value
        return result

    @api.multi
    def _compute_salary_adjustment(self, employee_id, contract_id=False,
                                   is_unique=False, return_record=False):
        # run for one payslip
        self.ensure_one()

        # Get the rules need to calculate
        rule_obj = self.env['hr.salary.rule']
        rule_domain = [('is_adjust', '=', True)]
        if not return_record:
            # If return_records, read all adjustable rules
            # If not, read global or local rules only
            rule_domain += [('is_unique_on_payslip', '=', is_unique)]
        rules = rule_obj.search(rule_domain)

        # Initial value for adjust_dict {salary rule code: 0, ...}
        adjust_dict = {}
        for rule in rules:
            adjust_dict[rule.code] = 0

        # Build domain to get adjustment records
        # in payslip period
        # for refund payslip
        # for given contract (only for local rule)
        # and the rules above (local or global rules)
        adjust_obj = self.env['hr.salary.adjustment']
        domain = [('date', '<=', self.date_to),
                  ('date', '>=', self.date_from),
                  ('employee_id', '=', employee_id),
                  ('rule_id', 'in', rules.ids)]
        if contract_id:
            # Add filter by contract for local rule
            domain += [('contract_id', '=', contract_id)]

        if not self.credit_note:
            # New payslip
            # Get adjustment records not paid
            domain += [('state', '=', 'new')]
        else:
            # In case refunding payslip
            # Get the paid adjustment records
            # to have the same amount of adjustment to refund
            domain += [('state', '=', 'paid')]

        adjust_records = adjust_obj.search(domain)
        if return_record:
            # use to update state to paid for salary adjustments
            # when approving payslip
            return adjust_records
        for adjust_record in adjust_records:
            adjust_dict[adjust_record.rule_id.code] += adjust_record.amount
        return adjust_dict

    @api.multi
    def compute_sheet(self):
        for payslip in self:
            # delete auto input lines
            payslip.input_line_ids.filtered(
                lambda l: l.is_from_contract).unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply
            # should be for all current contracts of the employee
            contract_ids = payslip.contract_id.ids or self.with_context(
                contract_state_condition=(
                    'state', 'in', ('open', 'close'))).get_contract(
                payslip.employee_id, payslip.date_from, payslip.date_to)
            # add input lines
            hr_contract_objs = self.env['hr.contract'].browse(contract_ids)
            days, hours = 0, 0
            for worked in payslip.worked_days_line_ids.filtered(
                    lambda w: w.code in ('WorkingDays', 'UnpaidL')):
                if worked.code == 'UnpaidL':
                    days -= worked.number_of_days
                    hours -= worked.number_of_hours
                else:
                    days += worked.number_of_days
                    hours += worked.number_of_hours
            if days or hours:
                for contract in hr_contract_objs:
                    for allowance in contract.allowance_ids:
                        if allowance.apply_on == 'hourly':
                            amount = allowance.amount * hours
                        elif allowance.apply_on == 'daily':
                            amount = allowance.amount * days
                        else:
                            amount = allowance.amount
                        name = allowance.code
                        if allowance.description:
                            name = allowance.description
                        payslip.input_line_ids.create(
                            {'name': name,
                                'code': allowance.code, 'amount': amount,
                                'contract_id': contract.id,
                                'payslip_id': payslip.id,
                                'is_from_contract': True})
        payslip_obj = self.with_context(
            contract_state_condition=('state', 'in', ('open', 'close')))
        return super(HrPayslip, payslip_obj).compute_sheet()

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(
                    localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in \
                localdict[
                'categories'].dict and \
                localdict[
                'categories'].dict[
                category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code,
            mainly for usability purposes
            """

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                        SELECT sum(amount) as sum
                        FROM hr_payslip as hp, hr_payslip_input as pi
                        WHERE hp.employee_id = %s AND hp.state = 'done'
                        AND hp.date_from >= %s AND hp.date_to <= %s
                        AND hp.id = pi.payslip_id AND pi.code = %s""", (
                    self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code,
            mainly for usability purposes
            """

            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                        SELECT sum(number_of_days) as number_of_days,
                        sum(number_of_hours) as number_of_hours
                        FROM hr_payslip as hp, hr_payslip_worked_days as pi
                        WHERE hp.employee_id = %s AND hp.state = 'done'
                        AND hp.date_from >= %s AND hp.date_to <= %s
                        AND hp.id = pi.payslip_id AND pi.code = %s""", (
                    self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code,
            mainly for usability purposes"""

            def sum(self, code, from_date=None, to_date=None,
                    contract_types=None, previous_payslip=None,
                    current_payslip=None, working_seniority=False):
                """
                @param code: code of payslip line to sum
                @param date_from, date_to: get payslip in this period
                    If not date_to, get today
                @param contract_types: only sum of payslip lines with
                    given contract types
                """
                sql = """
                    SELECT
                        SUM(CASE WHEN hp.credit_note = False
                        THEN (pl.total) ELSE (-pl.total) END)\
                    FROM hr_payslip hp
                    JOIN hr_payslip_line pl ON hp.id = pl.slip_id
                    LEFT JOIN hr_contract hc ON hc.id = pl.contract_id
                    LEFT JOIN hr_contract_type hct ON hc.type_id = hct.id
                    WHERE hp.employee_id = %s
                    AND hp.state = 'done'
                    AND pl.code = '%s'
                """ % (self.employee_id, code)
                if previous_payslip and current_payslip:
                    # Get total amount salary rule from previous payslip
                    sql += """
                        AND hp.date_to < '%s'
                        GROUP BY hp.date_from, hp.name
                        ORDER BY hp.date_from DESC
                    """ % (current_payslip.date_from)
                else:
                    # Get total amount from payslip in given period
                    # (from_date, to_date)
                    if not from_date:
                        from_date = datetime.now().strftime('%Y-%m-%d')
                    if not to_date:
                        to_date = datetime.now().strftime('%Y-%m-%d')
                    sql += """
                        AND hp.date_from >= '%s' AND hp.date_to <= '%s'
                        """ % (from_date, to_date)
                    if contract_types:
                        sql += """
                            AND hct.name in (%s)
                        """ % ','.join(map(str, contract_types))
                    if working_seniority:
                        sql += """AND hct.count_working_seniority = 't' """
                self.env.cr.execute(sql)
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        # we keep a dict with the result because a value can be
        # overwritten by another rule with the same code
        result_dict = {}
        rules_dict = {}
        categories_dict = {}
        payslip = self.env['hr.payslip'].browse(payslip_id)
        employee = payslip.employee_id
        payslip_obj = Payslips(employee.id, payslip, self.env)

        # Calculate remaining leaves = allocation request - leave days
        # with leave types defined in param default_remaining_leave_type
        hol_status_obj = self.env['hr.holidays.status']
        hol_obj = self.env['hr.holidays']
        param = self.env['ir.config_parameter'].sudo().get_param(
            'default_remaining_leave_type') or None
        hol_status_ids = hol_status_obj.search([('name', 'in', eval(param))])
        allo_days = hol_obj.compute_allo_days(employee.id, hol_status_ids)
        leave = hol_obj.compute_leave_days(employee.id, hol_status_ids)
        remaining_leaves = allo_days - leave[0]
        contracts = self.env['hr.contract'].browse(contract_ids)
        sorted_unique_rule_ids = []
        globaldict = {
            'contract_qty': len(contracts),
            'remaining_leaves': remaining_leaves,
            'employee': employee,
            'payslip': payslip_obj,
        }

        structure_obj = self.env['hr.payroll.structure']
        for contract in contracts:
            """
                For each contract
                    - Compute localdict
                    - Get all structure
                    - Get all rules of structure
                Compute globaldict is sum of value of all localdicts
            """
            # Reset blacklist
            blacklist = []
            # Salary inputs specify for each contract
            worked_days = {}
            for worked_days_line in payslip.worked_days_line_ids:
                if contract.id == worked_days_line.contract_id.id:
                    worked_days[worked_days_line.code] = worked_days_line
            inputs = {}
            for input_line in payslip.input_line_ids:
                if not input_line.code in inputs.keys():
                    inputs[input_line.code] = 0
                if contract.id == input_line.contract_id.id:
                    inputs[input_line.code] += input_line.amount

            input_obj = InputLine(employee.id, inputs, self.env)
            worked_days_obj = WorkedDays(employee.id, worked_days, self.env)
            rules_obj = BrowsableObject(employee.id, rules_dict, self.env)
            categorie_obj = BrowsableObject(employee.id, {}, self.env)

            localdict = {
                'employee': employee,
                'contract': contract,
                'categories': categorie_obj,
                'rules': rules_obj,
                'payslip': payslip_obj,
                'worked_days': worked_days_obj,
                'inputs': input_obj}
            # Add total adjust amount group by salary rule to localdict
            adjustdict = payslip._compute_salary_adjustment(
                employee.id, contract_id=contract.id)

            # Get structure on payslip
            # If not, get structure on contract
            if payslip.struct_id:
                structure_ids = list(
                    set(payslip.struct_id._get_parent_structure().ids))
            else:
                structure_ids = contract.get_all_structures()
            # get the rules of the structure and thier children
            rule_ids = structure_obj.browse(
                structure_ids).get_all_rules_unique()
            # run the rules by sequence
            sorted_rule_ids = []
            for rule in sorted(rule_ids, key=lambda x: x[1]):
                if not rule[2]:
                    sorted_rule_ids.append(rule[0])
                else:
                    if rule[0] not in sorted_unique_rule_ids:
                        sorted_unique_rule_ids.append(rule[0])
            sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

            for rule in sorted_rules:
                payslip_line = self._prepare_payslip_line(rule, employee.id,
                                                          contract.id)
                """
                For the normal rules
                Use the original OpenERP source code
                """
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0

                # Recompute adjustdict for each rule calculation
                localdict_copy = localdict.copy()
                adjustdict = adjustdict and localdict_copy.update(
                    adjustdict) or localdict_copy

                # check if the rule can be applied
                if rule._satisfy_condition(
                        localdict) and rule.id not in blacklist:
                    # compute the amount of the rule
                    amount, qty, rate = rule._compute_rule(adjustdict)

                    """Compute rule that using localdict """
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[
                        rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in
                    # the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(
                        localdict, rule.category_id,
                        tot_rule - previous_amount)

                    # create/overwrite the rule in the temporary results
                    payslip_line.update(
                        {'amount': amount, 'quantity': qty, 'rate': rate, })
                    result_dict[key] = payslip_line

                    """
                    Compute globaldict:
                    sum of amount of rule that has the same code
                    """
                    globaldict[rule.code] = globaldict.get(rule.code,
                                                           0) + tot_rule
                else:
                    # blacklist this rule and its children
                    blacklist += [id for id, seq in
                                  rule._recursive_search_of_rules()]

            # Write localdict['categories'].dict of all contracts
            categories_dict[contract.id] = localdict['categories'].dict

        # COMPUTE GLOBEL RULES
        # Compute globaldict['categories']
        adjustdict = payslip._compute_salary_adjustment(employee.id,
                                                        is_unique=True)
        globaldict['categories'] = BrowsableObject(employee.id, self.sumdict(
            categories_dict.values()), self.env)

        sorted_unique_rules = self.env['hr.salary.rule'].browse(
            sorted_unique_rule_ids)
        for rule in sorted_unique_rules:
            """
            Using globaldict instead of localdict
            """
            # TODO: to remove contract_id for global rule
            payslip_line = self._prepare_payslip_line(rule, employee.id)
            key = rule.code
            globaldict['result'] = None
            globaldict['result_qty'] = 1.0

            # Recompute adjustdict for each rule calculation
            globaldict_copy = globaldict.copy()
            adjustdict = adjustdict and globaldict_copy.update(
                adjustdict) or globaldict_copy
            # check if the rule can be applied
            if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                """Compute global rules using globaldict """
                # compute the amount of the rule
                # Use adjustdict to compute to get value of adjusted rule and
                # to avoid value of adjusted rule is plused to previous_amount
                amount, qty, rate = rule._compute_rule(adjustdict)
                # check if there is already a rule computed with that code
                previous_amount = rule.code in globaldict and globaldict[
                    rule.code] or 0.0
                # set/overwrite the amount computed for this rule
                # in the globaldict
                tot_rule = amount * qty * rate / 100.0
                globaldict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                globaldict = _sum_salary_rule_category(
                    globaldict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results
                payslip_line.update(
                    {'amount': amount, 'quantity': qty, 'rate': rate, })
                result_dict[key] = payslip_line
            else:
                # blacklist this rule and its children
                blacklist += [id for id, seq in
                              rule._recursive_search_of_rules()]

        return result_dict.values()

    @api.multi
    def action_payslip_done(self):
        """
        Override Function
        Change state to paid for salary adjust records in payslip period
        """
        for payslip in self:
            if not payslip.credit_note:
                adjust_records = payslip._compute_salary_adjustment(
                    payslip.employee_id.id, return_record=True)
                adjust_records.write(
                    {'state': 'paid', 'payslip_id': payslip.id})
        return super(HrPayslip, self).action_payslip_done()

    @api.multi
    def unlink(self):
        not_draft_contract = self.filtered(lambda obj: obj.state != 'draft')
        if not_draft_contract:
            raise ValidationError(_("You only can delete draft contract!"))
        try:
            return super(HrPayslip, self).unlink()
        except:
            raise ValidationError(_("This payslip is being used. You "
                                    "cannnot delete it."))
