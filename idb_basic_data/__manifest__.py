# -*- coding: utf-8 -*-
{
    'name': "基础资料",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "vision lu",
    'website': "https://www.idb.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/base_menu.xml',
        'views/product.xml',
        'views/product_category.xml',
        'views/res_partner.xml',
        'views/product_attribute.xml',
        'views/create_product_template.xml',
        'views/purchase.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

