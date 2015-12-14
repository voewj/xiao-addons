# -*- coding: utf-8 -*-
{
    'name': 'VISBP 财务收单',
    'author': 'Xiao',
    'category': 'visbp',
    'description': """
    财务部门收单，按会计期间收取统计客户的原始单据，并记录明细。
    """,
    'depends': ['base', 'visbp_custom'],
    'application': True,
    'data': ['security/visbp_security.xml',
             'security/ir.model.access.csv',
             'views/shoudan_view.xml',
             'views/partner_view.xml',
             'views/visbp_partner_wizard.xml',
             ],

}