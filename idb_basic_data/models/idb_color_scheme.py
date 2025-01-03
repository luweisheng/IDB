# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IdbProductAccessoryType(models.Model):
    _name = 'idb.product.accessory.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Color scheme'

    name = fields.Char(string='Color project name', translate=True)
    code = fields.Char(string='encoding', translate=True)
    # 显示顺序
    sequence = fields.Integer(string='Display sequence')