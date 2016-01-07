# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp import exceptions
import logging

_logger	=	logging.getLogger(__name__)
class Partner(models.Model):
    _inherit = 'res.partner'

    kuaiji = fields.Many2one('res.users', string='会计')
    type2 = fields.Selection([('nsr', '一般纳税人'), ('xgm', '小规模')], string='纳税人类别', default='xgm')
    caizhika = fields.Boolean(string="财智卡", help='如果客户财智卡在我公司请打勾！')
    liushi  = fields.Boolean(string='流失', default=False)
    geshui_line = fields.One2many('visbp.geshui', 'partner_id', string='个税名单')

class Geshui(models.Model):
    _name = 'visbp.geshui'

    name = fields.Char(string='姓名', required=True)
    code = fields.Char(string='身份证', size=18)
    gongzi = fields.Float(string='工资')
    is_active = fields.Boolean(string='在职', default=True)
    partner_id = fields.Many2one('res.partner', string='公司', domain=[('is_company', '=', True)])


class partnerWizard(models.TransientModel):
    _name = 'visbp.partner.wizard'

    partner_ids = fields.Many2many('res.partner', string='客户')
    new_kuaiji = fields.Many2one('res.users', string='指派会计')

    @api.multi
    def set_kuaiji(self):
        self.ensure_one()
        if not self.new_kuaiji:
            raise exceptions.ValidationError('请选择会计！')
        if self.new_kuaiji:
            self.partner_ids.write({'kuaiji': self.new_kuaiji.id})
        return True
    @api.multi
    def reopen_form(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new'}
    @api.multi
    def get_new(self):
        self.ensure_one()
        Partner = self.env['res.partner']
        New = Partner.search([('kuaiji', '=', False), ('is_company', '=', True)])
        self.partner_ids = New
        return self.reopen_form()


