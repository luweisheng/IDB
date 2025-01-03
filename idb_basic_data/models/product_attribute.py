# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# 产品标准化模板
class IdbProductAttributeTemplate(models.Model):
    _name = 'idb.product.attribute.template'
    _description = 'Product standardization template'

    name = fields.Char(string='Name', translate=True)
    # 模板明细
    product_attribute_line = fields.One2many('idb.product.attribute.template.line', 'product_attribute_template_id', string='Template detail')


class IdbProductAttributeTemplateLine(models.Model):
    _name = 'idb.product.attribute.template.line'

    name = fields.Char(string='Name', translate=True)
    product_attribute_template_id = fields.Many2one('idb.product.attribute.template', string='Product standardization template')
    product_attribute_id = fields.Many2one('idb.product.attribute', string='Stats')
    product_attribute_value_id = fields.Many2one('idb.product.attribute.value', string='Stats Value')


class IdbProductAttributeLine(models.Model):
    _name = 'idb.product.attribute'
    _description = 'Stats'

    # 属性名称
    name = fields.Char(string='Name', translate=True)
    # 属性值
    value_line = fields.One2many('idb.product.attribute.value', 'product_attribute_id', string='Stats Value')


class IdbProductAttributeValue(models.Model):
    _name = 'idb.product.attribute.value'
    _description = 'Stats Value'

    name = fields.Char(string='Name', translate=True)
    product_attribute_id = fields.Many2one('idb.product.attribute', string='Stats')


class IdbCreateProductTemplate(models.TransientModel):
    _name = 'idb.create.product.template'
    _description = 'Create a Product Template'

    name = fields.Char(string='Name', translate=True)
    product_attribute_template_id = fields.Many2one('idb.product.attribute.template', string='Product standardization template')

    @api.onchange('product_attribute_template_id')
    def _onchange_product_attribute_template_id(self):
        if self.product_attribute_template_id:
            value_line = []
            for line in self.product_attribute_template_id.product_attribute_line:
                value_line.append((0, 0, {'name': line.name, 'product_attribute_id': line.product_attribute_id.id}))
            self.value_line = value_line

    category_id = fields.Many2one('product.category', string='Product category')

    # 采购单位
    po_uom_id = fields.Many2one('uom.uom', string='Purchasing unit')
    # 库存单位
    uom_id = fields.Many2one('uom.uom', string='Stock keeping unit')

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            self.po_uom_id = self.category_id.po_uom_id.id
            self.uom_id = self.category_id.uom_id.id

    # 属性值
    value_line = fields.One2many('idb.create.product.template.line', 'create_product_template_id', string='Attribute detail')

    def create_product(self):
        # 关闭弹窗
        return {'type': 'ir.actions.act_window_close'}


class IdbCreateProductTemplateLine(models.TransientModel):
    _name = 'idb.create.product.template.line'
    _description = 'Create product template details'

    name = fields.Char(string='Name', translate=True)
    create_product_template_id = fields.Many2one('idb.create.product.template', string='Create Product Template')
    # 属性
    product_attribute_id = fields.Many2one('idb.product.attribute', string='Stats')
    # 属性值
    product_attribute_value_id = fields.Many2one('idb.product.attribute.value',
                                                 string='Value',
                                                 domain='[("product_attribute_id", "=", product_attribute_id)]')

