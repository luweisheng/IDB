# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Category name already exists, do not create!')
    ]

    barcode = fields.Char(string='encoding', translate=True)
    # 海关码
    customs_code = fields.Char(string='Customs code', translate=True)

    # 采购单位
    po_uom_id = fields.Many2one('uom.uom', string='Purchasing unit')
    # 库存单位
    uom_id = fields.Many2one('uom.uom', string='Stock keeping unit')
    # 工程单位
    eng_uom_id = fields.Many2one('uom.uom', string='Engineering unit')

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(ProductCategory, self).copy({'name': self.name + '(copy)'})
        return res

    # 物料损耗明细表
    material_loss_ids = fields.One2many('idb.material.loss', 'category_id', string='Material loss schedule')


class IdbMaterialLoss(models.Model):
    _name = 'idb.material.loss'
    _description = 'Material loss schedule'

    category_id = fields.Many2one('product.category', string='Product classification')
    # 序号
    sequence = fields.Integer(string='Serial number')
    # 开始数量
    start_qty = fields.Float(string='Initial quantity')
    # 结束数量
    end_qty = fields.Float(string='End quantity')
    # 损耗率
    loss_rate = fields.Float(string='Attrition rate')

