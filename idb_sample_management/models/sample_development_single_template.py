# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SampleDevelopmentSingleTemplate(models.Model):
    _name = 'sample.development.single.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sample development single template'

    name = fields.Char(string='ID', default="New")
    # 描述
    description = fields.Text(string='Description')
    # 模板明细
    sample_development_single_template_line_ids = fields.One2many('sample.development.single.template.line',
                                                                  'sample_development_single_template_id',
                                                                  string='Template detail')


class SampleDevelopmentSingleTemplateLine(models.Model):
    _name = 'sample.development.single.template.line'
    _description = 'Sample development single template details'

    sequence = fields.Integer(string='Serial number')
    sample_development_single_template_id = fields.Many2one('sample.development.single.template', string='Sample development single template')
    # 产品分类
    accessory_id = fields.Many2one('idb.product.accessory.type', string='category')
    # 必填
    is_required = fields.Boolean(string='required')
    # category_id = fields.Many2one('product.category', string='类别')