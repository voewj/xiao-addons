import time
from openerp import api, fields, models

class AccountBalance(models.AbstractModel):
    _name = 'report.visbp_todo.report_visbp_account_balance'

    @api.multi
    def render_html(self, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('visbp_todo.report_visbp_account_balance')
        docargs = {
            'doc_ids': self.ids,
            'doc_models': self.model,
            'docs': docs,
#            'data': data['form']['user_data'],
            'data': data['form'],
        }
        return report_obj.render('visbp_todo.report_visbp_account_balance', docargs)