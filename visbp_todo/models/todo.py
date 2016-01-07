# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp import exceptions
import time
import openerp.addons.decimal_precision as dp


class Partner(models.Model):
    _inherit = 'res.partner'

    code = fields.Integer(string='客户编号')
#    not_active = fields.Boolean(string='流失', default=False)
class Kaizhang(models.Model):
    _name = 'visbp.kaizhang'

    name = fields.Char(string="名称", required=True, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string="客户", readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='处理人', readonly=True, states={'draft': [('readonly', False)]}, default=lambda self:self.env.uid)
    line_ids = fields.One2many('visbp.kaizhang.line', 'kaizhang_id', string="凭证行", readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', '草稿'), ('done', '开帐')], default='draft')
    period_id = fields.Many2one('account.period', string="开帐期间", required=True, readonly=True, states={'draft': [('readonly', False)]})
    @api.one
    def action_done(self):
        res = self.env['visbp.kaizhang.line'].search([('kaizhang_id', '=', self.id), ('period_id', '=', self.period_id.id)])
        c_t = sum(a.credit_total for a in res)
        d_t = sum(a.debit_total for a in res)
        q_d = sum(a.qichu_debit for a in res)
        q_c = sum(a.qichu_credit for a in res)
        if c_t == d_t and q_d == q_c:
            self.write({'state': 'done'})
        else:
            raise exceptions.ValidationError('不平衡，无法开帐！')
#    @api.one
#    def action_compute(self):
class KaizhangLine(models.Model):
    _name = 'visbp.kaizhang.line'

    account_id = fields.Many2one('account.account', string='会计科目', required=True)
    debit_total = fields.Float(string='累计借方')
    credit_total = fields.Float(string='累计贷方')
    kaizhang_id = fields.Many2one('visbp.kaizhang', string='开帐分录')
    partner_id = fields.Many2one('res.partner', related='kaizhang_id.partner_id', string='客户')
    period_id = fields.Many2one('account.period', string='开帐期间', related='kaizhang_id.period_id')
    qichu_debit = fields.Float(string='期初借方余额')
    qichu_credit = fields.Float(string='期初贷方余额')

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

    @api.one
    def get_shoudan_state(self):
        if self.shoudan_id:
            field_ref = self.env['visbp.shoudan'].fields_get(allfields='state')
            selection = dict(field_ref['state']['selection'])
            state_string = selection[self.shoudan_id.state]
            self.ref = '%s:%s' % (state_string,self.shoudan_id.name)

    name = fields.Char(string='任务', default='/')
    user_id = fields.Many2one('res.users', string='会计', related='partner_id.kuaiji', store=True, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', related='shoudan_id.partner_id', stroe=True, string='客户', readonly=True, states={'draft': [('readonly', False)]}, required=True)
    start_date = fields.Date(string='开始期间', readonly=True, states={'draft': [('readonly', False)]})
    end_date = fields.Date(string='截止期间', readonly=True, states={'draft': [('readonly', False)]})
    period_id = fields.Many2one('account.period', string='会计期间', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', '草稿'), ('bs', '待报税'), ('jz', '待记账'), ('done', '完成')], default='draft', readonly=True)
    partner_code = fields.Integer(string='客户编号', related='partner_id.code', store=True, readonly=True)
    pingzheng_line = fields.One2many('visbp.pingzheng', 'todo_id', string='帐务')
    baoshui_line = fields.One2many('visbp.baoshui', 'todo_id', string='报税')
    pingzheng_count = fields.Integer(string='记账', compute=count_all_pingzheng)
    baoshui_count = fields.Integer(string='报税', compute=count_all_baoshui)
    shoudan_id = fields.Many2one('visbp.shoudan', string='收单号')
    ref = fields.Char(string='引用', compute=get_shoudan_state)

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
    code = fields.Integer(string='记字', default='0', readonly=True, states={'draft': [('readonly', False)]})
    pingzheng_ids = fields.One2many('visbp.pingzheng.line', 'pingzheng_id', string='凭证行', readonly=True, states={'draft': [('readonly', False)]})
    todo_id = fields.Many2one('visbp.todo', string='任务', readonly=True, states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', related='todo_id.user_id', string='会计', store=True, readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', related='todo_id.partner_id', string='客户', store=True, readonly=True, states={'draft': [('readonly', False)]})
    credit_total = fields.Float(string='贷方合计', compute=_get_total, digits=dp.get_precision('Account'))
    debit_total = fields.Float(string='借方合计', compute=_get_total, digits=dp.get_precision('Account'))
    process_date = fields.Date(string='日期', default=fields.Date.context_today)
    period_id = fields.Many2one('account.period', related='todo_id.period_id', store=True, readonly=True, states={'draft': [('readonly', False)]})


    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            period = self.env['account.period'].search([('id', '=', vals['period_id'])]).name
            partner = self.env['res.partner'].search([('id', '=', vals['partner_id'])]).name
            vals['name'] = '%s:%s' % (period, partner)
        partner_id = vals.get('partner_id')
        period_id = vals.get('period_id')
        total = self.env['visbp.pingzheng'].search_count([('partner_id', '=', partner_id), ('period_id', '=', period_id)])
        vals['code'] = total + 1
#        elif not (self.period_id or self.partner_id):
#            raise exceptions.Warning('请选择客户或期间！')
#            vals['code'] = self.env['ir.sequence'].next_by_code('visbp.pingzheng') or '0'

        res = super(Pingzhen, self).create(vals)
        return res


class Pingzhenline(models.Model):
    _name = 'visbp.pingzheng.line'

    name = fields.Char(string='摘要')
    account_id = fields.Many2one('account.account', string='会计科目')
    credit = fields.Float(string='贷方金额', digits=dp.get_precision('Account'))
    debit = fields.Float(string='借方金额', digits=dp.get_precision('Account'))
    pingzheng_id = fields.Many2one('visbp.pingzheng', string='凭证')
    partner_id = fields.Many2one('res.partner', related='pingzheng_id.partner_id', store=True)
    period_id = fields.Many2one('account.period', related='pingzheng_id.period_id', store=True)

class baoshui(models.Model):
    _name = 'visbp.baoshui'




    name = fields.Char(string='名称', default='/')
    period_id = fields.Many2one('account.period', related='todo_id.period_id', store=True)
    partner_id = fields.Many2one('res.partner', related='todo_id.partner_id', string='客户', store=True)
    gs_image = fields.Binary(string='国税')
    ds_image = fields.Binary(string='地税')
    todo_id = fields.Many2one('visbp.todo', string='任务')
    user_id = fields.Many2one('res.users', string='会计', default=lambda self: self.env.uid)

#    shouru_lines = fields.One2many('visbp.shouru', 'baoshui_id', string='收入明细')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            period = self.env['account.period'].search([('id', '=', vals.get('period_id', False))]).name
            partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id', False))]).name
            vals['name'] = '%s:%s' % (period, partner)
        res = super(baoshui, self).create(vals)
        return res
