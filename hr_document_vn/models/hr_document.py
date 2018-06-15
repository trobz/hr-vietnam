# -*- coding: utf-8 -*-
# Copyright 2009-2018 Trobz (http://trobz.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models, api


class HrDocument(models.Model):
    _name = "hr.document"

    name = fields.Char(string='ID / Number', required=True)
    active = fields.Boolean(string='Active', default=True)
    type_id = fields.Many2one('hr.document.type', string='Type', required=True)
    emp_id = fields.Many2one('hr.employee', string='Employee', required=True)
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    issue_place = fields.Char(size=128, string='Issue Place')
    issue_by = fields.Char(size=128, string='Issue By')
    mandatory_issue_date = fields.Boolean(string='Mandatory Issue Date')
    mandatory_expiry_date = fields.Boolean(string='Mandatory Expiry Date')
    mandatory_issue_place = fields.Boolean(string='Mandatory Issue Place')
    mandatory_issue_by = fields.Boolean(string='Mandatory Issue By')
    expired = fields.Boolean(string='Expired', compute="_expired")

    @api.onchange('type_id')
    def _mandatory_fields(self):
        if self.type_id:
            self.mandatory_issue_date = self.type_id.mandatory_issue_date
            self.mandatory_expiry_date = self.type_id.mandatory_expiry_date
            self.mandatory_issue_place = self.type_id.mandatory_issue_place
            self.mandatory_issue_by = self.type_id.mandatory_issue_by

    @api.multi
    def _expired(self):
        for record in self:
            record.expired = record.expiry_date \
                and record.expiry_date < fields.Date.today() \
                and True or False

    @api.model
    def get_doc_expiring_30_days(self):
        res = []
        today = fields.Date.today()
        next_30_days = (fields.Date.from_string(today) +
                        timedelta(days=30)).strftime("%Y-%m-%d")
        employees = self.env['hr.employee'].search([])
        doc_types = self.env['hr.document.type'].search([])
        for emp in employees:
            for doc_type in doc_types:
                # Get latest doc
                docs = self.search([('expiry_date', '>=', today),
                                    ('expiry_date', '<=',
                                     next_30_days), ('emp_id', '=', emp.id),
                                    ('type_id', '=', doc_type.id)],
                                   order="expiry_date DESC")
                renewal_docs = self.search([('emp_id', '=', emp.id),
                                            ('type_id', '=', doc_type.id),
                                            ('expiry_date', '>',
                                             next_30_days)])
                if renewal_docs:
                    continue
                if docs:
                    res.append(docs[0])
        return res

    @api.model
    def get_doc_expired(self):
        res = []
        today = fields.Date.today()
        employees = self.env['hr.employee'].search([])
        doc_types = self.env['hr.document.type'].search([])
        for emp in employees:
            for doc_type in doc_types:
                # Get latest doc
                docs = self.search([('expiry_date', '<', today),
                                    ('emp_id', '=', emp.id),
                                    ('type_id', '=', doc_type.id)],
                                   order="expiry_date DESC")
                renewal_docs = self.search([('emp_id', '=', emp.id),
                                            ('type_id', '=', doc_type.id),
                                            ('expiry_date', '>', today)])
                if renewal_docs:
                    continue
                if docs:
                    res.append(docs[0])
        return res
