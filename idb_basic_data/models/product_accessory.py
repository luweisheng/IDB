# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IdbProductAccessory(models.Model):
    _name = 'idb.product.accessory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product accessories'

    # 物料编号
    code = fields.Char(string='Material number', track_visibility='always')
    # 名称
    name = fields.Char(string='Name', default='_New', track_visibility='always', translate=True)
    # 产品主色
    main_color_id = fields.Many2one('idb.product.color', string='Product main color', track_visibility='always')
    # 主料
    main_product_id = fields.Many2one('product.product', string='Product staple', track_visibility='always')
    # 配料明细
    accessory_line_ids = fields.One2many('idb.product.accessory.line', 'accessory_id', string='Batching detail')


class IdbProductAccessoryLine(models.Model):
    _name = 'idb.product.accessory.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product accessories details'

    accessory_id = fields.Many2one('idb.product.accessory', string='Product accessories')
    # 名称
    name = fields.Char(string='Name', translate=True)
    product_id = fields.Many2one('product.product', string='Product')
    category_id = fields.Many2one('product.category', string='Category')
    # 颜色
    color_id = fields.Many2one('idb.product.color', string='Colour')



