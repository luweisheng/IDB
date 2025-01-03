# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BatchModificationColorMatchingMaterials(models.TransientModel):
    _name = 'batch.modification.color.matching.materials'
    _description = 'Batch modification of color matching materials'

    name = fields.Char(string='name', default='Batch modification of color matching materials', translate=True)
    materials_line_ids = fields.One2many('batch.modification.color.matching.materials.line', 'batch_id',
                                         string='Material store')

    def batch_modification_color_matching_materials(self):
        bom_id = self.env['mrp.bom'].browse(self.env.context.get('bom_id'))
        if bom_id:
            for line in self.materials_line_ids:
                update_data = {}
                # 修改该配色项目的物料颜色
                bom_line_ids = bom_id.bom_line_ids.filtered(lambda x: x.accessory_id == line.accessory_id)
                if line.color_id:
                    update_data['color_id'] = line.color_id.id
                if line.product_id:
                    update_data['product_id'] = line.product_id.id
                if update_data:
                    bom_line_ids.write(update_data)
        return {'type': 'ir.actions.act_window_close'}


class BatchModificationColorMatchingMaterialsLine(models.TransientModel):
    _name = 'batch.modification.color.matching.materials.line'
    _description = 'Batch modification color matching material line'

    batch_id = fields.Many2one('batch.modification.color.matching.materials', string='Batch modification of color matching materials')
    # 配色项目
    accessory_id = fields.Many2one('idb.product.accessory.type', string='Color scheme')
    # 颜色
    color_id = fields.Many2one('idb.product.color', string='colour')
    product_id = fields.Many2one('product.product', string='materiel', domain=[('material_type', '=', 'material')])


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    name = fields.Char(string='name', copy=False, index=True, default=lambda self: _('New'))
    # 产品主色
    main_color_id = fields.Many2one('idb.product.color', string='Product main color', track_visibility='onchange')
    # 产品配色
    match_color_id = fields.Many2one('idb.product.color', string='Product color matching', track_visibility='onchange')
    # 纸格编号
    grid_number = fields.Char(string='Grid number', track_visibility='onchange', translate=True)
    factory_number = fields.Char(string='Factory model number', track_visibility='onchange', translate=True)
    # 款号版本
    factory_version = fields.Char(string='Model number version', track_visibility='onchange', translate=True)
    # 产品分类
    category_id = fields.Many2one('product.category', string='Product classification', domain=[('parent_id', '=', '成品')])
    barcode = fields.Char(string='Product number', related='product_id.barcode')
    # 产品材质
    material_id = fields.Char(string='Product material', track_visibility='onchange', translate=True)
    # 客户
    customer_id = fields.Many2one('res.partner', string='Customer name', track_visibility='onchange',
                                  domain=[('customer_rank', '>', 0)])
    # 客户款号
    customer_number = fields.Char(string='Customer account number', track_visibility='onchange', translate=True)

    image1 = fields.Binary("Image1")
    image2 = fields.Binary("Image2")
    image3 = fields.Binary("Image3")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'mrp.bom') or _("New")
        return super(MrpBom, self).create(vals_list)

    no_bom_line_ids = fields.One2many('no.mrp.bom.line', 'bom_id', string='No BOM material is available')

    def batch_modification_color_matching_materials(self):
        batch_id = self.env['batch.modification.color.matching.materials'].create({
            'materials_line_ids': [(0, 0, {'accessory_id': i}) for i in self.bom_line_ids.accessory_id.ids],
        })
        return {
            'name': _('Batch modification of color matching materials'),
            'type': 'ir.actions.act_window',
            'res_model': 'batch.modification.color.matching.materials',
            'view_mode': 'form',
            'context': {'bom_id': self.id},
            'res_id': batch_id.id,
            'target': 'new',
        }

    def set_color_table(self):
        # 获取bom_line配色项目accessory_id，重新赋值color_configuration
        accessory_ids = self.partial_detail_ids.mapped('accessory_id') + self.no_bom_line_ids.mapped('accessory_id')
        color_configuration = ''
        tr_01 = ''
        for accessory_id in accessory_ids:
            color_configuration += f'<td>{accessory_id.name}</td>'
            accessory_id = self.partial_detail_ids.filtered(
                lambda x: x.accessory_id == accessory_id) or self.no_bom_line_ids.filtered(
                lambda x: x.accessory_id == accessory_id)
            if accessory_id:
                color_id = accessory_id[0].color_id
                if color_id:
                    color_name = color_id.name
                    tr_01 += f'<td>{color_name}</td>'
                else:
                    tr_01 += f'<td class="o_data_cell cursor-pointer o_field_cell o_list_many2one"></td>'
            else:
                tr_01 += f'<td></td>'
        self.color_configuration = f"""
            <table class="table table-sm table-bordered w-100 text-center color_bom">
                <tr>
                    <td>Product main color</td>
                    <td>Product color matching</td>
                    {color_configuration}
                </tr>
                <tr>
                    <td>{self.main_color_id.name or ''}</td>
                    <td>{self.match_color_id.name or ''}</td>
                    {tr_01}
                </tr>
            </table>
        """

    color_configuration = fields.Html(string='Color configuration')
    table_data = fields.Json(string='Table Data')

    def _compute_grouped_data(self):
        # 获取mrp_bom_line的数据
        mrp_bom_lines = self.bom_line_ids.read_group(
            [('product_id', '!=', False)],  # 查询条件
            ['product_id', 'product_qty:sum'],  # 按字段分组并汇总
            ['product_id']  # 分组字段
        )

        # 获取no_mrp_bom_line的数据
        no_mrp_bom_lines = self.no_bom_line_ids.read_group(
            [('product_id', '!=', False)],  # 查询条件
            ['product_id', 'product_qty:sum'],  # 按字段分组并汇总
            ['product_id']  # 分组字段
        )

        # 合并数据
        result = {}
        for line in mrp_bom_lines:
            product_id = line['product_id'][0]
            result[product_id] = result.get(product_id, 0) + line['product_qty']

        for line in no_mrp_bom_lines:
            product_id = line['product_id'][0]
            result[product_id] = result.get(product_id, 0) + line['product_qty']

        return result

    # 部位明细
    partial_detail_ids = fields.One2many('partial.detail.line', 'bom_id', string='Position detail')

    def generate_color_matching_bom(self):
        color_configuration = self.color_configuration
        if color_configuration:
            # 整理color_configuration信息，正则匹配，只获取class带有color_bom的table里面的数据
            color_bom = re.search(
                r'<table class="table table-sm table-bordered w-100 text-center color_bom">.*?</table>',
                color_configuration, re.S)
            if color_bom:
                color_bom = color_bom.group()
                # 获取表格数据
                table_data = []
                trs = re.findall(r'<tr>.*?</tr>', color_bom, re.S)
                if trs and len(trs) >= 2:
                    for tr in trs:
                        tds = re.findall(r'<td>(.*?)</td>', tr)
                        table_data.append(tds)
                    # 检查配色项目是否有修改
                    accessory_ids = self.partial_detail_ids.mapped('accessory_id') + self.no_bom_line_ids.mapped(
                        'accessory_id')
                    accessory_name = [accessory_id.name for accessory_id in accessory_ids]
                    color_configuration_accessory = table_data[0][3:]
                    # 求差集
                    diff = list(set(accessory_name) ^ set(color_configuration_accessory))
                    if diff:
                        raise UserError(_('The color matching item has been modified, please reset the color table!'))

                else:
                    raise UserError(_('Color table data error!'))
            else:
                raise UserError(_('Please set the color chart first!'))
        else:
            pass

    # 配料与主色相同
    def update_bom_line(self):
        self.bom_line_ids = None
        bom_line_ids = {}
        for partial_detail_id in self.partial_detail_ids:
            product_id = partial_detail_id.product_id.id
            partial_detail_stock_use = partial_detail_id.partial_detail_stock_use
            accessory_id = partial_detail_id.accessory_id.id
            if product_id not in bom_line_ids:
                bom_line_ids[product_id] = [partial_detail_stock_use, accessory_id]
            else:
                bom_line_ids[product_id][0] += partial_detail_stock_use
        for no_mrp_bom_line in self.no_bom_line_ids:
            product_id = no_mrp_bom_line.product_id.id
            production_quantity = no_mrp_bom_line.production_quantity
            accessory_id = no_mrp_bom_line.accessory_id.id
            if product_id not in bom_line_ids:
                bom_line_ids[product_id] = [production_quantity, accessory_id]
            else:
                bom_line_ids[product_id][0] += production_quantity
        self.bom_line_ids = [(0, 0, {
            'product_id': product_id,
            'product_qty': bom_line_ids[product_id][0],
            'accessory_id': bom_line_ids[product_id][1]
        }) for product_id in bom_line_ids]

    # 预估数量
    estimate_quantity = fields.Integer(string='Estimated quantity')

    # 与产品主色相同
    def same_as_main_color(self):
        color_configuration = self.color_configuration
        if color_configuration:
            # 整理color_configuration信息，正则匹配，只获取class带有color_bom的table里面的数据
            color_bom = re.search(
                r'<table class="table table-sm table-bordered w-100 text-center color_bom">.*?</table>',
                color_configuration, re.S)
            if color_bom:
                color_bom = color_bom.group()
                # 获取表格数据
                table_data = []
                trs = re.findall(r'<tr>.*?</tr>', color_bom, re.S)
                if trs and len(trs) >= 2:
                    for tr in trs[1:]:
                        tds = re.findall(r'<td>(.*?)</td>', tr)
                        table_data.append(tds)


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_id = fields.Many2one(required=False, domain=[('material_type', '=', 'material')])
    category_id = fields.Many2one('product.category', related='product_id.categ_id')

    part_selection = fields.Selection([('yes', 'Have parts'), ('no', 'positionless')], string='Part/no part', default='yes',
                                      required=True)
    # 显示顺序
    sequence = fields.Integer(string='Display sequence')
    # 配色项目
    accessory_id = fields.Many2one('idb.product.accessory.type', string='Color scheme')
    # 物料编号
    barcode = fields.Char(string='Material number', related='product_id.barcode')
    # 物料类型
    material_type = fields.Selection(related='product_id.product_tmpl_id.material_type')
    # 贴合类型
    fit_type = fields.Selection([('single', 'monolayer'), ('composite', 'recombination')], string='type', required=True,
                                default='single')
    # 规格
    specification = fields.Char(string='specification', translate=True)
    # 工程单位
    engineering_uom_id = fields.Many2one('uom.uom', related='product_id.product_tmpl_id.engineering_uom_id')
    # 工程系数
    engineering_coefficient = fields.Float(related='product_id.product_tmpl_id.engineering_coefficient')
    # 库存单位
    product_uom_id = fields.Many2one(required=False)
    # 颜色
    color_id = fields.Many2one('idb.product.color', string='colour')
    # 部位
    position = fields.Char(string='position', translate=True)
    # 核对
    check = fields.Boolean(string='collate')
    # 生产增加损耗
    production_add_loss = fields.Float(string='Production increase loss')
    # 计料
    count_material = fields.Boolean(string='Material count')
    # 加工前和加工后物料匹配顺序
    match_sequence = fields.Integer(string='Matching sequence')
    # 备注
    note = fields.Text(string='remark')

    product_qty = fields.Float(digits='Stock Unit')


class PartialDetailLine(models.Model):
    _name = 'partial.detail.line'
    _inherit = 'mrp.bom.line'
    _description = 'Part detail BOM material'

    # 长度
    length = fields.Float(string='Length', digits='length_unit')
    # 宽度
    width = fields.Float(string='Breadth', digits='width_unit')

    partial_detail_stock_use = fields.Float(string='Inventory unit usage',
                                            compute='_compute_partial_detail_stock_use',
                                            digits='Stock Unit')

    @api.depends('length', 'width', 'engineering_coefficient')
    def _compute_partial_detail_stock_use(self):
        for line in self:
            length, width = line.length, line.width
            if width > 0:
                # 面积
                area = length * width
            else:
                area = line.length
            if line.engineering_coefficient <= 0:
                line.partial_detail_stock_use = area
            else:
                line.partial_detail_stock_use = area / line.engineering_coefficient

    # 排刀类型
    knife_type = fields.Selection([('draft', 'No automatic cutting'), ('double', 'Transverse exclusion length')], string='Cutter type')
    # 刀数
    knife_count = fields.Integer(string='Number of cuts')
    # 排刀用量
    knife_use = fields.Float(string='Tooling usage')
    # 库存单位排刀用量
    stock_knife_use = fields.Float(string='Inventory unit row usage')
    # 物料有效宽幅
    material_width = fields.Float(string='Effective width')
    # 物料有效长度
    material_length = fields.Float(string='Effective length')
    # 余料宽幅
    residue_width = fields.Float(string='Spare material width')
    # 余料长度
    residue_length = fields.Float(string='Residual length')
    # 加工类型
    process_type = fields.Selection([('cut', 'tailor'), ('sew', 'Make up'), ('package', 'package')], string='Processing type')


class NoMrpBomLine(models.Model):
    _name = 'no.mrp.bom.line'
    _inherit = 'mrp.bom.line'
    _description = 'No BOM material is available'

    # 生产用量
    production_quantity = fields.Float(string='Inventory unit usage',
                                       compute='_compute_production_quantity',
                                       digits='Stock Unit')

    @api.depends('product_qty', 'engineering_coefficient')
    def _compute_production_quantity(self):
        for line in self:
            engineering_coefficient = line.engineering_coefficient
            if engineering_coefficient:
                line.production_quantity = line.product_qty / engineering_coefficient
            else:
                line.production_quantity = 0


class IdbMergeBomLine(models.Model):
    _name = 'idb.merge.bom.line'
    _description = 'Combined BOM material'

    name = fields.Char(string='Name', default='Combined BOM material', translate=True)
