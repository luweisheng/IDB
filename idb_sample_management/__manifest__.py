# -*- coding: utf-8 -*-
{
    'name': "Sample management",

    'summary': "",

    'description': """
        Sample management
    """,

    'author': "IDB",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['idb_basic_data'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_product.xml',
        'views/sample_management.xml',
        'views/sample_development_single_template.xml',
        'views/promise_group.xml',
        'views/reject_reason.xml',
        'views/idb_sample_score.xml',
        'wizard/idb_development_schedule.xml',
        'views/mrp_plm.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    # 'assets': {
    #     'web.assets_backend': [
    #         'idb_sample_management/static/src/views/fields/many2one/*',
    #     ],
    # },
}
