# -*- coding:utf-8 -*-
from openerp import api, fields, models

class Shoudan(models.Model):
    _name = 'visbp.shoudan'

    name = fields.Char(string='单号', default='New', states={'draft': [('readonly', 'False')]}, readonly=True)
    user_id = fields.Many2one('res.users', string='处理人', default=lambda self: self.env.uid, states={'draft': [('readonly', 'False')]}, readonly=True)
    partner_id = fields.Many2one('res.partner', string='客户', required=True, states={'draft': [('readonly', 'False')]}, readonly=True)
    shoudan_lines = fields.One2many('visbp.shoudan.line', 'shoudan_id', string='收单明细', states={'draft': [('readonly', 'False')]}, readonly=True)
    state = fields.Selection([('draft', '草稿'), ('confirm', '已移交'), ('cancel', '取消')], default='draft')
    kuaiji_id = fields.Many2one(string='会计', related='partner_id.kuaiji', store=True, readonly=True)
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('shoudan') or 'New'
        res = super(Shoudan, self).create(vals)
        return res

    @api.one
    def set_cancel(self):
        return self.write({'state': 'cancel'})

    @api.one
    def set_confirm(self):
        return self.write({'state': 'confirm'})

class shoudanLine(models.Model):
    _name = 'visbp.shoudan.line'

    name = fields.Selection([('sb', '社保'), ('sr', '收入'), ('yh', '银行'), ('fy', '费用')], string='单据', default='sb')
    type = fields.Selection([('qq', 'QQ'), ('email', 'Email'), ('kd', '邮寄')], string='收单方式')
    code = fields.Integer(string='快递单号', help="请输入快递单号!")
    month = fields.Date(string='期间', required=True, default=fields.Date.context_today)
    shoudan_id = fields.Many2one('visbp.shoudan', string='收单号')
    partner_id = fields.Many2one('res.partner', related='shoudan_id.partner_id', string='客户')
    shouru_line = fields.One2many('visbp.shouru', 'line_id', string='收入明细')
    kuaiji_id = fields.Many2one(string='会计', related='partner_id.kuaiji', store=True, readonly=True)
class shouru(models.Model):
    _name = 'visbp.shouru'

    name=fields.Selection([('gs', '国税'), ('ds', '地税')], string='名称', required=True)
    type =fields.Selection([('dk', '代开'), ('zk', '自开')], string='类型')
    total = fields.Float(string='金额')
    line_id = fields.Many2one('visbp.shoudan.line', string='收单明细')
    month = fields.Date(string='期间', related='line_id.month')
