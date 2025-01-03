# -*- coding: utf-8 -*-
{
    'name': "Basic data",

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
    'depends': ['mail', 'web', 'mrp_plm', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/decimal_precision.xml',
        'views/base_menu.xml',
        'views/product_color.xml',
        'views/idb_color_scheme.xml',
        'views/product_accessory.xml',
        'views/product.xml',
        'views/product_category.xml',
        'views/product_uom.xml',
        'views/res_partner.xml',
        'views/product_attribute.xml',
        'views/create_product_template.xml',
        'views/purchase.xml',
        'views/batch_modification_color_matching_materials.xml',
        'views/mrp_bom.xml',
        'views/matching_color_bom.xml',
        'views/mrp_plm.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'idb_basic_data/static/src/js/show_one2many.js',
    #     ],
    # }
}
