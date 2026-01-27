# -*- coding: utf-8 -*-
{
    'name': 'Project Task Template',
    'version': '1.0',
    'summary': 'Brief description of the module',
    'description': '''
        Detailed description of the module
    ''',
    'depends': ['base', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_task_template_views.xml',
        'views/project_task.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}