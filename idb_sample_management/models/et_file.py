# -*- coding: utf-8 -*-
import base64
import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IdbSampleManagement(models.Model):
    _inherit = 'idb.sample.management'

    # et文件列表
    et_file_ids = fields.One2many('idb.et.file', 'sample_id', string='ET file list')


class IdbEtFile(models.Model):
    _name = 'idb.et.file'
    _description = 'ET file'

    name = fields.Char(string='Filename')
    sequence = fields.Integer(string='Serial number')
    file = fields.Binary(string='File', attachment=True)
    file_name = fields.Char(string='Filename', compute='_compute_file_name')
    bom_id = fields.Many2one('mrp.bom', string='Product BOM')
    bom_date = fields.Datetime(string='BOM Date')

    @api.depends('file')
    def _compute_file_name(self):
        for record in self:
            if record.file:
                record.file_name = record.name
            else:
                record.file_name = False

    sample_id = fields.Many2one('idb.sample.management', string='sample')

    def _get_excel_file(self):
        file_content = self.file
        if not file_content:
            raise UserError(_("Please upload ET file"))
        # Decode the file content
        file_data = base64.b64decode(file_content)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(1)
        partial_detail_ids = []
        no_bom_line_ids = []
        accessory_ids = self.env['idb.product.accessory.type'].search([])
        accessory = {item.name: item.id for item in accessory_ids}
        sample_id = self.sample_id
        # 配色项目
        other_materials = ('辅料', '织带', '拉链')
        for row_idx in range(5, sheet.nrows):
            position_line_row_data = {}
            no_position_line_row_data = {}
            row = sheet.row(row_idx)
            color_scheme = row[0].value
            # color_scheme去除数字
            color_scheme = ''.join([i for i in color_scheme if not i.isdigit()])
            materials = row[1].value
            if not materials:
                continue
            if not color_scheme:
                break
            # 宽幅
            specification = row[10].value
            position = row[2].value
            # 复合物料
            composite_material = row[3].value
            quantity = row[6].value
            if color_scheme != '五金':
                position_line_row_data['specification'] = specification
                # 单层物料、复合物料
                materials_type = 'single'
                position_line_row_data['position'] = position
                if composite_material:
                    materials_type = 'composite'
                    position_line_row_data['position'] += composite_material
                if specification:
                    position_line_row_data['fit_type'] = materials_type
                if color_scheme in accessory:
                    accessory_id = accessory[color_scheme]
                else:
                    accessory_id = self.env['idb.product.accessory.type'].create({'name': color_scheme}).id
                accessory[color_scheme] = accessory_id
                position_line_row_data['accessory_id'] = accessory[color_scheme]
                if color_scheme in other_materials:
                    product_id = self.env['product.product'].search([('name', 'ilike', materials), ('material_type', '=', 'material')], limit=1)
                    if not product_id:
                        # product_id = None
                        categ_id = self.env['product.category'].search([('name', 'ilike', color_scheme)], limit=1)
                        if not categ_id:
                            categ_id = self.env['product.category'].create({'name': color_scheme})
                        product_id = self.env['product.product'].create({'name': materials,
                                                                         'categ_id': categ_id.id,
                                                                         'detailed_type': 'product'})
                    product_id = product_id.id
                else:
                    sample_management_line_id = sample_id.sample_management_line_ids.filtered(
                    lambda x: x.accessory_id.name == color_scheme)
                    product_id = sample_management_line_id.main_product_id.id
                    # 样品单主色
                    position_line_row_data['color_id'] = sample_management_line_id.main_color_id.id or None
                # 样品单主料
                position_line_row_data['product_id'] = product_id
                position_line_row_data['length'] = row[4].value
                position_line_row_data['width'] = row[5].value
                position_line_row_data['product_qty'] = quantity
                position_line_row_data['knife_use'] = row[7].value
                position_line_row_data['specification'] = specification
                partial_detail_ids.append(position_line_row_data)
            else:
                product_id = self.env['product.product'].search([('name', 'ilike', materials), ('material_type', '=', 'material')], limit=1)
                if not product_id:
                    categ_id = self.env['product.category'].search([('name', 'ilike', color_scheme)], limit=1)
                    if not categ_id:
                        categ_id = self.env['product.category'].create({'name': color_scheme})
                    product_id = self.env['product.product'].create({'name': materials,
                                                                     'categ_id': categ_id.id,
                                                                     'detailed_type': 'product'})
                    # no_position_line_row_data['product_id'] = None

                no_position_line_row_data['product_id'] = product_id.id
                no_position_line_row_data['accessory_id'] = accessory[color_scheme]
                no_position_line_row_data['product_qty'] = quantity
                no_position_line_row_data['part_selection'] = 'no'
                no_bom_line_ids.append(no_position_line_row_data)
        return partial_detail_ids, no_bom_line_ids

    def create_product_bom_data(self):
        partial_detail_ids, no_bom_line_ids = self._get_excel_file()
        # 创建BOM主产品， BOM主产品 = 款号 + * + 1 + *  + 产品材质 + * + 产品颜色
        factory_number = self.sample_id.factory_number
        # 主料
        main_product_name = self.sample_id.sample_management_line_ids.filtered(
            lambda x: x.accessory_id.name == '主料').main_product_id.name
        product_name = factory_number + '*' + '1' + '*' + main_product_name + '*' + self.sample_id.color_id.name
        category_id = self.sample_id.category_id.id
        product_id = self.env['product.product'].search([('name', '=', product_name)], limit=1)
        if not product_id:
            product_id = self.env['product.product'].create({'name': product_name,
                                                             'categ_id': category_id,
                                                             'detailed_type': 'product'})
        # 创建BOM
        bom_id = self.env['mrp.bom'].create({
            'product_id': product_id.id,
            'product_tmpl_id': product_id.product_tmpl_id.id,
            'category_id': category_id,
            'main_color_id': self.sample_id.color_id.id,
            'sample_id': self.sample_id.id,
            'partial_detail_ids': [(0, 0, line) for line in partial_detail_ids],
            'no_bom_line_ids': [(0, 0, line) for line in no_bom_line_ids],
        })
        today = fields.Datetime.now()
        self.write({'bom_id': bom_id.id, 'bom_date': today})
        self.sample_id.bom_id = bom_id.id
        bom_id.update_bom_line()
