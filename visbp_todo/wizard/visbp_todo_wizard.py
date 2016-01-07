# -*- coding: utf-8 -*-
from openerp import api, fields, models, exceptions
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class pzwizard(models.TransientModel):
    _name = 'visbp.guozhang'

    partner_id = fields.Many2one('res.partner', string='客户')
    period_id = fields.Many2one('account.period', string='期间')
    pingzheng_ids = fields.Many2many('visbp.pingzheng', string='凭证')

    @api.multi
    def do_pass(self):
        self.ensure_one()
        domain = [('partner_id', '=', self.partner_id.id), ('period_id', '=', self.period_id.id), ('state', '=', 'draft')]
        res = self.env['visbp.pingzheng'].search(domain)
        total = self.env['visbp.pingzheng'].search_count(domain)
        if not res:
            raise exceptions.ValidationError('没有凭证记录！')
        for o in res:
            if o.credit_total != o.debit_total:
                raise exceptions.Warning(_('记字 %s 号凭证借贷不平衡') % o.code)
        _logger.warning('更新凭证数量： %s', total)
        res.write({'state': 'post'})
        return True

