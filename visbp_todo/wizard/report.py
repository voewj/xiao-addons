# -*- coding: utf-8 -*-

from openerp import api, fields, models, exceptions

class AccountBalance(models.TransientModel):
    _name = 'visbp.balance'

    period_from = fields.Many2one('account.period', string='开始期间', required=True)
    period_end = fields.Many2one('account.period', string='结束期间', required=True)
    partner_id = fields.Many2one('res.partner', string='客户', required=True)

    @api.multi
    def get_data(self):
        account_period = self.env['account.period'].search([])
        res = {}
        year = self.period_from.name[3:]
        month_from = int(self.period_from.name[0:2])
        month_end = int(self.period_end.name[0:2])
        pingzheng = self.env['visbp.pingzheng.line'].search([('partner_id', '=', self.partner_id.id)])
        kz = self.env['visbp.kaizhang.line'].search([('partner_id', '=', self.partner_id.id)])
        period = []
        if month_from > month_end:
            raise exceptions.ValidationError('开始期间不能大于结束期间！')
        elif month_from == month_end:
            pz = pingzheng.search([('period_id', '=', self.period_from.id)])
#            kz = self.env['visbp.kaizhang.line'].search([('partner_id', '=', self.partner_id.id)])
            res[self.period_from.name] = {}
            for line in pz:
                credit_total = sum(a.credit for a in pz if a.account_id.id == line.account_id.id)
                debit_total = sum(a.debit for a in pz if a.account_id.id == line.account_id.id)
                yearcredit_total = sum(a.credit for a in pingzheng if a.account_id.id == line.account_id.id and int(a.period_id.name[0:2]) <= month_end)
                yeardebit_total = sum(a.debit for a in pingzheng if a.account_id.id == line.account_id.id and int(a.period_id.name[0:2]) <= month_end)
#                res[line.period_id.name] = {}
                res[line.period_id.name][line.account_id.code] = {}
                res[line.period_id.name][line.account_id.code]['name'] = line.account_id.name
                res[line.period_id.name][line.account_id.code]['credit_total'] = credit_total
                res[line.period_id.name][line.account_id.code]['debit_total'] = debit_total
                res[line.period_id.name][line.account_id.code]['yearcredit_total'] = yearcredit_total
                res[line.period_id.name][line.account_id.code]['yeardebit_total'] = yeardebit_total
                qimo_total = kz.search([('account_id', '=', line.account_id.id)]).qichu_debit - kz.search([('account_id', '=', line.account_id.id)]).qichu_credit + yeardebit_total - yearcredit_total
                res[line.period_id.name][line.account_id.code]['qimo_total'] = qimo_total
                if qimo_total or credit_total or debit_total:
                    qichu_total = qimo_total + credit_total - debit_total
                    res[line.period_id.name][line.account_id.code]['qichu_total'] = qichu_total
#                if line.period_id.name == kz.period_id.name:
#                    res[line.period_id.name][line.account_id.code]['qichu_debit'] = kz.qichu_debit
#                    res[line.period_id.name][line.account_id.code]['qichu_credit'] = kz.qichu_credit
#                elif line.period_id.name > kz.period_id.name:

            res[self.period_from.name] = sorted(res[self.period_from.name].iteritems(), key=lambda data:data[0], reverse=False)
            res = sorted(res.iteritems(), key=lambda data:data[0], reverse=False)

        else:
            for p in range(month_from, month_end+1):
                period_name = str(p).rjust(2,'0') + '/' + year
                period.append(period_name)
            for p in period:
                period_id = account_period.search([('name', '=', p)])
                pz = pingzheng.search([('period_id', '=', period_id.id)])
#                kz = self.env['visbp.kaizhang.line'].search([('partner_id', '=', self.partner_id.id)])
                res[p] = {}
                for line in pz:
                    credit_total = sum(a.credit for a in pz if a.account_id.id == line.account_id.id)
                    debit_total = sum(a.debit for a in pz if a.account_id.id == line.account_id.id)
                    yearcredit_total = sum(a.credit for a in pingzheng if a.account_id.id == line.account_id.id and int(a.period_id.name[0:2]) <= int(p[0:2]))
                    yeardebit_total = sum(a.debit for a in pingzheng if a.account_id.id == line.account_id.id and int(a.period_id.name[0:2]) <= int(p[0:2]))
#                    res[line.period_id.name] = {}
                    res[p][line.account_id.code] = {}
                    res[p][line.account_id.code]['name'] = line.account_id.name
                    res[p][line.account_id.code]['credit_total'] = credit_total
                    res[p][line.account_id.code]['debit_total'] = debit_total
                    res[line.period_id.name][line.account_id.code]['yearcredit_total'] = yearcredit_total
                    res[line.period_id.name][line.account_id.code]['yeardebit_total'] = yeardebit_total
                    qimo_total = kz.search([('account_id', '=', line.account_id.id)]).qichu_debit - kz.search([('account_id', '=', line.account_id.id)]).qichu_credit + yeardebit_total - yearcredit_total
                    res[line.period_id.name][line.account_id.code]['qimo_total'] = qimo_total
                    if qimo_total or credit_total or debit_total:
                        qichu_total = qimo_total + credit_total - debit_total
                        res[line.period_id.name][line.account_id.code]['qichu_total'] = qichu_total

                res[p] = sorted(res[p].iteritems(), key=lambda data:data[0], reverse=False)
            res = sorted(res.iteritems(), key=lambda data:data[0], reverse=False)
        return res

#        for period in account_period:
#            p = int(period.name[0:2])
#        if month_from > month_end:
#            raise exceptions.ValidationError('开始期间不能大于结束期间！')
#        elif month_from == month_end:
#            rec = pingzheng.search([('period_id', '=', self.period_from.id)])
#            for line in rec:
#                credit_total = sum(a.credit for a in rec  if a.account_id.id == line.account_id.id)
#                debit_total = sum(a.debit for a in rec if a.account_id.id == line.account_id.id)
#                res[line.period_id.name] = {}
#                res[line.period_id.name][line.account_id.name] = {}
#                res[line.period_id.name][line.account_id.name]['code'] = line.account_id.code
#                res[line.period_id][line.account_id.name]['credit_total'] = credit_total
#                res[line.period_id][line.account_id.name]['credit_total'] = debit_total
#        else:
#        pingzheng = self.env['visbp.pingzheng.line'].search([('partner_id', '=', self.partner_id.id), ('period_id', '=', self.period_from.id)])
#        for line in pingzheng:
#            credit_total = sum(a.credit for a in pingzheng if a.account_id.id == line.account_id.id)
#            debit_total = sum(a.debit for a in pingzheng if a.account_id.id == line.account_id.id)
#            res[line.account_id.name] = {}
#            res[line.account_id.name]['code'] = line.account_id.code
#            res[line.account_id.name]['credit_total'] = credit_total
#            res[line.account_id.name]['debit_total'] = debit_total
#        return res

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        rec = self.read(['period_from', 'period_end', 'partner_id'])[0]
        if rec.get('id',False):
            data['ids']=[rec['id']]
#       data['form'] = rec
#        user_data = self.get_data(data)
        data['form'] = self.get_data()
#        data['form']['user_data'] = user_data
        return self.env['report'].with_context(Portrait=True).get_action(self, 'visbp_todo.report_visbp_account_balance', data=data)
