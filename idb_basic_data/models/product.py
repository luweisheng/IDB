# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # 工程单位
    engineering_uom_id = fields.Many2one('uom.uom', string='工程单位')
    # 工程系数
    engineering_coefficient = fields.Float(string='工程系数')

    # 生产损耗
    production_loss = fields.Float(string='生产损耗')
    # 采购损耗
    purchase_loss = fields.Float(string='采购损耗')
    # 报价损耗
    quote_loss = fields.Float(string='报价损耗')
    # 参考进价
    reference_price = fields.Float(string='参考进价')
    # 参考售价
    reference_sale_price = fields.Float(string='参考售价')