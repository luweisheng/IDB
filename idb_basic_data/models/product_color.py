# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError


# 配色表
class IdbProductColor(models.Model):
    _name = 'idb.product.color'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Color table'

    name = fields.Char(string='Color name', translate=True)
    code = fields.Char(string='Color numbering', translate=True)
    # 英文颜色
    en_name = fields.Char(string='English color', translate=True)
    # 备注
    note = fields.Char(string='remark', translate=True)