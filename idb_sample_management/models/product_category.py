# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    _sql_constraints = [('name_uniq', 'unique(name)', 'Category names must be unique')]

    # 产品分类
    sort_selection = fields.Selection([('finished_product', 'Finished product'),
                                       ('semi_finished_product', 'Semi-finished product'),
                                       ('raw_material', 'Raw material'),
                                       ('accessory', 'attachment'),
                                       ('other', 'other')], string='sort', default='finished_product', required=True)

    parent_name = fields.Char(string='Parent class', default='ALL')

    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            self.parent_name = self.parent_id.name
        else:
            self.parent_name = 'ALL'

#     # 下级类别
#     child_ids = fields.One2many('product.category.line', 'parent_id', string='下级类别')
#
#
# class ProductCategoryLine(models.Model):
#     _name = 'product.category.line'
#     _description = '下级类别'
#
#     parent_id = fields.Many2one('product.category', string='上级类别')
#     name = fields.Many2one('product.category', string='类别')
#     sequence = fields.Integer(string='序号')