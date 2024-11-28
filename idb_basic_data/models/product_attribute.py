# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# 产品标准化模板
class IdbProductAttributeTemplate(models.Model):
    _name = 'idb.product.attribute.template'
    _description = '产品标准化模板'

    name = fields.Char(string='名称')
    # 模板明细
    product_attribute_line = fields.One2many('idb.product.attribute.template.line', 'product_attribute_template_id', string='模板明细')


class IdbProductAttributeTemplateLine(models.Model):
    _name = 'idb.product.attribute.template.line'

    name = fields.Char(string='名称')
    product_attribute_template_id = fields.Many2one('idb.product.attribute.template', string='产品标准化模板')
    product_attribute_id = fields.Many2one('idb.product.attribute', string='属性')
    product_attribute_value_id = fields.Many2one('idb.product.attribute.value', string='属性')

    # text commit


class IdbProductAttributeLine(models.Model):
    _name = 'idb.product.attribute'
    _description = '属性'

    # 属性名称
    name = fields.Char(string='名称')
    # 属性值
    value_line = fields.One2many('idb.product.attribute.value', 'product_attribute_id', string='属性值')


class IdbProductAttributeValue(models.Model):
    _name = 'idb.product.attribute.value'
    _description = '属性值'

    name = fields.Char(string='名称')
    product_attribute_id = fields.Many2one('idb.product.attribute', string='属性')


class IdbCreateProductTemplate(models.TransientModel):
    _name = 'idb.create.product.template'
    _description = '创建产品模板'

    name = fields.Char(string='名称')
    product_attribute_template_id = fields.Many2one('idb.product.attribute.template', string='产品标准化模板')

    @api.onchange('product_attribute_template_id')
    def _onchange_product_attribute_template_id(self):
        if self.product_attribute_template_id:
            value_line = []
            for line in self.product_attribute_template_id.product_attribute_line:
                value_line.append((0, 0, {'name': line.name, 'product_attribute_id': line.product_attribute_id.id}))
            self.value_line = value_line

    category_id = fields.Many2one('product.category', string='产品类别')

    # 采购单位
    po_uom_id = fields.Many2one('uom.uom', string='采购单位')
    # 库存单位
    uom_id = fields.Many2one('uom.uom', string='库存单位')

    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            self.po_uom_id = self.category_id.po_uom_id.id
            self.uom_id = self.category_id.uom_id.id

    # 属性值
    value_line = fields.One2many('idb.create.product.template.line', 'create_product_template_id', string='属性明细')

    def create_product(self):
        # 关闭弹窗
        return {'type': 'ir.actions.act_window_close'}


class IdbCreateProductTemplateLine(models.TransientModel):
    _name = 'idb.create.product.template.line'
    _description = '创建产品模板明细'

    name = fields.Char(string='名称')
    create_product_template_id = fields.Many2one('idb.create.product.template', string='创建产品模板')
    # 属性
    product_attribute_id = fields.Many2one('idb.product.attribute', string='属性')
    # 属性值
    product_attribute_value_id = fields.Many2one('idb.product.attribute.value',
                                                 string='值',
                                                 domain='[("product_attribute_id", "=", product_attribute_id)]')

