# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # 交货日期
    delivery_date = fields.Date(string='Delivery date')
    # 采购类型
    idb_purchase_type = fields.Selection([('main', 'Main material purchase'),
                                          ('normal', 'General stores purchasing'),
                                          ('sale', 'Sales order'),
                                          ('manual_operation', 'Manual operation')],
                                         string='Type of purchase', default='manual_operation', required=True)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    category_id = fields.Many2one('product.category', related='product_id.categ_id', string='category', store=True)
    barcode = fields.Char(string='Bar code', related='product_id.barcode', store=True)
    # 交货日期
    delivery_date = fields.Date(string='Delivery date')