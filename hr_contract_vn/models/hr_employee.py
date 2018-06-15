# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import Warning


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    contract_ids = fields.One2many('hr.contract', 'employee_id')

    @api.multi
    @api.depends(
        'contract_ids.date_start',
        'contract_ids.type_id',
        'contract_ids.employee_id'
    )
    def _compute_hire_date(self):
        """
        Compute hired date is the contract start date of:
            + The first contract
            + The new contract that has the time between this contract
            and nearest contract is over 1 days
        """
        contract_obj = self.env['hr.contract']

        # Start calculate hire_date
        for employee in self:
            contracts = contract_obj.search(
                [('employee_id', '=', employee.id),
                 ('type_id.count_working_seniority', '=', True)],
                order='date_start DESC')
            if not contracts:
                continue

            # First contract
            hire_date = contracts[-1].date_start

            # New first contract after stopping working and coming back.
            while len(contracts) > 1:
                if not contracts[1].date_end:
                    # The previous contract is a unlimited contract
                    # This contract must be ended
                    raise Warning(
                        _("The previous contract (ID: %s, %s) should be ended \
                        before create a new contract"
                          % (contracts[1].id, contracts[1].name)))

                contract = contracts[0]
                previous_end = datetime.strptime(contracts[1].date_end, DF)
                next_start = datetime.strptime(contract.date_start, DF)
                if (next_start - previous_end).days > 1:
                    hire_date = contract.date_start
                    break
                contracts -= contract

            # Store hire_date value
            employee.hire_date = hire_date

    hire_date = fields.Date(
        compute=_compute_hire_date, store=True, string='Hired Date',
        help="This field use to calculate the working seniority of an employee"
        ", get stating date of the first contract with contract type"
        " with field `Count on working seniority` activated")
