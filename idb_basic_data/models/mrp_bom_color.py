# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class IdbMrpBomColor(models.Model):
    _name = 'idb.mrp.bom.color'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'BOM Color table'

    bom_id = fields.Many2one('mrp.bom', string='BOM')
    # 产品主色
    main_color_id = fields.Many2one('idb.product.color', string='Product main color', track_visibility='onchange')
    # 产品配色
    color_id = fields.Many2one('idb.product.color', string='Product color matching', track_visibility='onchange')
    # 配色明细
    color_line_ids = fields.One2many('idb.mrp.bom.color.line', 'bom_color_id', string='Color matching detail')

    @api.model
    def default_get(self, fields):
        res = super(IdbMrpBomColor, self).default_get(fields)
        # 根据BOM配色项目创建明细配色项目
        bom_id = self.env['mrp.bom'].browse(self.env.context.get('bom_id'))
        accessory_ids = bom_id.bom_line_ids.accessory_id.ids + bom_id.no_bom_line_ids.accessory_id.ids
        color_line_ids = [(0, 0, {'accessory_id': accessory_id}) for accessory_id in accessory_ids]
        res['color_line_ids'] = color_line_ids
        return res


class IdbMrpBomColorLine(models.Model):
    _name = 'idb.mrp.bom.color.line'
    _description = 'BOM matching color indicates fine'

    bom_color_id = fields.Many2one('idb.mrp.bom.color', string='Color scheme chart')
    # 配色项目
    accessory_id = fields.Many2one('idb.product.accessory.type', string='Color scheme')
    # 颜色
    color_id = fields.Many2one('idb.product.color', string='Color')


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    # 颜色配色表
    color_line_ids = fields.One2many('idb.mrp.bom.color', 'bom_id', string='Color matching')


