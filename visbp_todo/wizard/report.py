# -*- coding: utf-8 -*-

from openerp import api, fields, models

class AccountBalance(models.Model):
    _name = 'visbp.balance'

    account_ids = fields.Many2many('account.account', 'visbp_account_balance', 'balance_id', 'account_id', string='科目')
    period_from = fields.Many2one('account.period', string='开始期间', required=True)
    period_end = fields.Many2one('account.period', string='结束期间', required=True)
    partner_id = fields.Many2one('res.partner', string='客户', required=True)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read()