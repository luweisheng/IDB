# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # 规格
    specification = fields.Char(string='specification', translate=True)

    def take_next_level(self):
        self.product_tmpl_id.take_next_level()

    def product_cancel(self):
        self.product_tmpl_id.product_cancel()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    _sql_constraints = [('name_uniq', 'unique(name)', 'The material name must be unique！')]
    category_barcode = fields.Char(related='categ_id.barcode', string='Class coding', store=True)
    # 工程单位
    engineering_uom_id = fields.Many2one('uom.uom', string='Engineering unit')
    # 工程系数
    engineering_coefficient = fields.Float(string='Engineering coefficient', default=1)
    # 生产损耗
    production_loss = fields.Float(string='Production loss')
    # 采购损耗
    purchase_loss = fields.Float(string='Procurement loss')
    # 报价损耗
    quote_loss = fields.Float(string='Quotation loss')
    # 参考进价
    reference_price = fields.Float(string='Reference purchase price')
    # 参考售价
    reference_sale_price = fields.Float(string='Reference selling price')

    detailed_type = fields.Selection(default='product')

    # 物料类型
    material_type = fields.Selection([
        ('material', 'material'),
        ('materials', 'Materials')
    ], string='Material type', default='material', required=True)

    # 颜色
    color_id = fields.Many2one('idb.product.color', string='colour')

    specification = fields.Char(string='specification', translate=True)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        res = super(ProductTemplate, self).copy({'name': self.name + '(copy)'})
        return res

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        # 库存单位、工程单位、采购单位默认等于类别里面的单位
        if not res.uom_id:
            res.uom_id = res.categ_id.uom_id.id
        if not res.engineering_uom_id:
            res.engineering_uom_id = res.categ_id.uom_id.id
        # barcode = 当前类别最大barcode + 1
        # barcode = self.env['product.product'].search_read([('categ_id', '=', res.categ_id.id)], ['barcode'], limit=1, order='barcode desc')
        # new_barcode =
        # if not res.purchase_uom_id:
        #     res.purchase_uom_id = res.categ_id.uom_id.id
        return res

    # 成本价
    cost_price = fields.Float(string='Cost price')

    # # PLM状态
    state = fields.Selection([('draft', 'concept'),
                              ('development', 'exploit'),
                              ('validation', 'verify'),
                              ('release', 'publish'),
                              ('sustaining', 'improvement'),
                              ('obsolete', 'Die out')
                              ], string='PLM status', default='draft')

    def take_next_level(self):
        state = {
            'draft': 'development',
            'development': 'validation',
            'validation': 'release',
            'release': 'sustaining',
        }
        self.state = state[self.state]

    def product_cancel(self):
        self.state = 'obsolete'



