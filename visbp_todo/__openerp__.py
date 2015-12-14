# -*- coding: utf-8 -*-
{
    'name': 'Visbp Todo',
    'author': 'Xiao',
    'descripion': """
    添加公司会计根据收单，或0收据给客户代理会计服务。
    """,
    'depends': ['visbp', 'account'],
    'data': ['views/visbp_todo_view.xml',
             'security/visbp_todo_security.xml',
             'security/ir.model.access.csv',
             ],
    'application': True,
}