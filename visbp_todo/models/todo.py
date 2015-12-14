# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp import exceptions
import time


class Partner(models.Model):
    _inherit = 'res.partner'

    code = fields.Integer(string='客户编号')
#    not_active = fields.Boolean(string='流失', default=False)
class Todo(models.Model):
    _name = 'visbp.todo'

    @api.one
    def count_all_pingzheng(self):
        self.pingzheng_count = self.env['visbp.pingzheng'].search_count([('todo_id', '=', self.id)])
        return True
    @api.one
    def count_all_baoshui(self):
        self.baoshui_count = self.env['visbp.baoshui'].search_count([('todo_id', '=', self.id)])
        return True

    name = fields.Char(string='任务', default='/')
    user_id = fields.Many2one('res.users', string='会计', default=lambda self: self.env.uid, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='客户', readonly=True, states={'draft': [('readonly', False)]}, required=True)
    start_date = fields.Date(string='开始期间', readonly=True, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='截止期间', readonly=True, states={'draft': [('readonly', False)]})
    period_id = fields.Many2one('account.period', string='会计期间', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', '草稿'), ('bs', '待报税'), ('jz', '待记账'), ('done', '完成')], default='draft', readonly=True)
    partner_code = fields.Integer(string='客户编号', related='partner_id.code', store=True, readonly=True)
    pingzheng_line = fields.One2many('visbp.pingzheng', 'todo_id', string='帐务')
    baoshui_line = fields.One2many('visbp.baoshui', 'todo_id', string='报税')
    pingzheng_count = fields.Integer(string='记账', compute=count_all_pingzheng)
    baoshui_count = fields.Integer(string='报税', compute=count_all_baoshui)

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('visbp.todo') or '/'
        res = super(Todo, self).create(vals)
        return res


    @api.one
    def do_done(self):
        if self.pingzheng_line and self.baoshui_line:
            return self.write({'state': 'done'})
        else:
            raise exceptions.ValidationError('有任务未完成！')

    @api.one
    def do_bs(self):
        if self.pingzheng_line:
            return self.write({'state': 'bs'})
        else:
            raise exceptions.ValidationError('请先完成记账！')

    @api.one
    def do_jz(self):
        if self.baoshui_line:
            return self.write({'state': 'jz'})
        else:
            raise exceptions.ValidationError('请先完成报税！')

class Pingzhen(models.Model):
    _name = 'visbp.pingzheng'

    @api.one
    @api.depends('pingzheng_ids.credit', 'pingzheng_ids.debit')
    def _get_total(self):
        self.credit_total = 0.0
        self.debit_total = 0.0
        res = self.pingzheng_ids.search([('pingzheng_id', '=', self.id)])
        self.credit_total = sum(line.credit for line in res)
        self.debit_total = sum(line.debit for line in res)
        return True

    name = fields.Char(string='Name', default='/')
    state = fields.Selection([('draft', '未过帐'), ('post', '过帐')],default='draft')
    code = fields.Integer(string='记字', default='1', readonly=True, states={'draft': [('readonly', False)]})
    pingzheng_ids = fields.One2many('visbp.pingzheng.line', 'pingzheng_id', string='凭证行', readonly=True, states={'draft': [('readonly', False)]})
    todo_id = fields.Many2one('visbp.todo', string='任务', readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', related='todo_id.user_id', string='会计', store=True, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', related='todo_id.partner_id', string='客户', store=True, readonly=True, states={'draft': [('readonly', False)]})
    credit_total = fields.Float(string='贷方合计', compute=_get_total)
    debit_total = fields.Float(string='借方合计', compute=_get_total)
    process_date = fields.Date(string='日期', default=fields.Date.context_today)
    period_id = fields.Many2one('account.period', related='todo_id.period_id', store=True, readonly=True, states={'draft': [('readonly', False)]})


    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            period = self.env['account.period'].search([('id', '=', vals['period_id'])]).name
            partner = self.env['res.partner'].search([('id', '=', vals['partner_id'])]).name
            vals['name'] = '%s:%s' % (period, partner)
        res = super(Pingzhen, self).create(vals)
        return res


class Pingzhenline(models.Model):
    _name = 'visbp.pingzheng.line'

    name = fields.Char(string='摘要')
    account_id = fields.Many2one('account.account', string='会计科目')
    credit = fields.Float(string='贷方金额')
    debit = fields.Float(string='借方金额')
    pingzheng_id = fields.Many2one('visbp.pingzheng', string='凭证')
    partner_id = fields.Many2one('res.partner', related='pingzheng_id.partner_id', store=True)

class baoshui(models.Model):
    _name = 'visbp.baoshui'

    name = fields.Char(string='名称', default='/')
    period_id = fields.Many2one('account.period', related='todo_id.period_id', store=True)
    partner_id = fields.Many2one('res.partner', related='todo_id.partner_id', string='客户', store=True)
    gs_image = fields.Binary(string='国税')
    ds_image = fields.Binary(string='地税')
    todo_id = fields.Many2one('visbp.todo', string='任务')
    user_id = fields.Many2one('res.users', string='会计', default=lambda self: self.env.uid)
