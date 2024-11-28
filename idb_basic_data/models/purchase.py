# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # 交货日期
    delivery_date = fields.Date(string='交货日期')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    category_id = fields.Many2one('product.category', related='product_id.categ_id', string='类别', store=True)
    barcode = fields.Char(string='条码', related='product_id.barcode', store=True)
    # 交货日期
    delivery_date = fields.Date(string='交货日期')