# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    barcode = fields.Char(string='编码')

    # 采购单位
    po_uom_id = fields.Many2one('uom.uom', string='采购单位')
    # 库存单位
    uom_id = fields.Many2one('uom.uom', string='库存单位')