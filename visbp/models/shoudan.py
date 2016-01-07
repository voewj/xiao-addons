# -*- coding:utf-8 -*-
from openerp import api, fields, models, exceptions
import time

class Shoudan(models.Model):
    _name = 'visbp.shoudan'
    _order = 'create_date desc'
    name = fields.Char(string='单号', default='New', states={'draft': [('readonly', 'False')]}, readonly=True)
    user_id = fields.Many2one('res.users', string='处理人', default=lambda self: self.env.uid, states={'draft': [('readonly', 'False')]}, readonly=True)
    partner_id = fields.Many2one('res.partner', string='客户',  states={'draft': [('readonly', 'False')]}, readonly=True)
    shoudan_lines = fields.One2many('visbp.shoudan.line', 'shoudan_id', string='收单明细', states={'draft': [('readonly', 'False')]}, readonly=True)
    state = fields.Selection([('draft', '草稿'), ('confirm', '已移交'), ('cancel', '取消')], default='draft')
    kuaiji_id = fields.Many2one(string='会计', related='partner_id.kuaiji', store=True, readonly=True)
    moth = fields.Integer(string='月份', default=time.localtime()[1])
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('shoudan') or 'New'
        res = super(Shoudan, self).create(vals)
        return res
    @api.multi
    def auto_all(self):
        partner = self.env['res.partner'].search([('liushi', '=', False), ('customer', '=', True)])
        moth_today = time.localtime()[1]
        res = self.env['visbp.shoudan']
        todo = self.env['visbp.todo']
        rec = res.search([('moth', '=', moth_today)])
        customer = []
        for r in rec:
            if r.partner_id not in customer:
                customer.append(r.partner_id.id)
        for c in partner:
            if c.id not in customer:
                shoudan_id = res.create({'partner_id': c.id,})
                todo_id = todo.create({'shoudan_id': shoudan_id.id,})
                
                    
#        customer = []
#        for c in partner:
#            customer.append(c.id)
#        for o in rec:
#            if o.partner_id in customer:
#                customer.remove(o.partner_id)
#        for i in customer:
#            shoudan_id = res.create({
#                'partner_id': i,
#            })
#            if c.id  not in customer:
#                shoudan_id = res.create({
#                    'partner_id': c.id,
#                })
#        return True
#        for c in partner:
#            rec = res.search([('partner_id', '=', c.id), ('moth', '=', moth_today)])
#            if rec:
#                raise exceptions.ValidationError('已全部更新！')
#            else:
#                shoudan_id = res.create({
#                    'partner_id': c.id,
#                })
#        return True


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
    period_id = fields.Many2one('account.period', string='期间')
#    month = fields.Date(string='期间', required=True, default=fields.Date.context_today)
    shoudan_id = fields.Many2one('visbp.shoudan', string='收单号')
    partner_id = fields.Many2one('res.partner', related='shoudan_id.partner_id', string='客户')
    shouru_line = fields.One2many('visbp.shouru', 'line_id', string='收入明细')
    kuaiji_id = fields.Many2one(string='会计', related='partner_id.kuaiji', store=True, readonly=True)

class shouru(models.Model):
    _name = 'visbp.shouru'

    @api.model
    def _get_period(self):
        line = self.env['visbp.shoudan.line'].browse(self._context.get('line_id', False))
        if line.period_id:
            return line.period_id.id

    @api.one
    def _get_baoshui(self):
        todo = self.env['visbp.todo']
        baoshui = self.env['visbp.baoshui']
        if self.line_id:
            shoudan = self.line_id.shoudan_id
            order = todo.search([('shoudan_id', '=', shoudan.id)])
            if order:
                bs_order = baoshui.search([('todo_id', '=', order.id)])
                if bs_order:
                    self.baoshui_id = bs_order
                    return True
                else:
                    bs_order = baoshui.create({'todo_id': order.id})
                    self.baoshui_id = bs_order




    name=fields.Selection([('gs', '国税'), ('ds', '地税')], string='名称', required=True)
    type =fields.Selection([('dk', '代开'), ('zk', '自开')], string='类型')
    fapiao = fields.Selection([('pupiao', '普票'), ('zhuanpiao', '专票')], string='增值税发票')
    product_type = fields.Selection([('service', '服务'), ('product', '货物')])
    total = fields.Float(string='金额')
    line_id = fields.Many2one('visbp.shoudan.line', string='收单明细')
#    month = fields.Date(string='期间', related='line_id.month')
    period_id = fields.Many2one('account.period', string='期间', default=lambda self: self._get_period())
    baoshui_id = fields.Many2one('visbp.baoshui', string='报税单', compute=_get_baoshui)