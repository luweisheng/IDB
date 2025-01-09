# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    def update_matching_color_bom(self):
        for line in self.color_line_ids:
            line.update_matching_color_bom()


class MatchingColorBom(models.Model):
    _name = 'matching.color.bom'
    _inherit = 'mrp.bom'
    _description = 'Color matching BOM'

    # 颜色BOM明细
    color_bom_line_ids = fields.One2many('matching.color.bom.line', 'matching_color_bom_id', string='Color BOM details')

    def update_matching_color_bom(self):
       pass


class MatchingColorBomLine(models.Model):
    _name = 'matching.color.bom.line'
    _inherit = 'mrp.bom.line'
    _description = 'Color BOM details'

    matching_color_bom_id = fields.Many2one('matching.color.bom', string='Color matching BOM')
    # 工程单位用量
    engineering_quantity = fields.Float(string='Engineering unit consumption')
    stock_quantity = fields.Float(string='Inventory unit usage', compute='_compute_stock_quantity')

    @api.depends('engineering_quantity', 'engineering_coefficient')
    def _compute_stock_quantity(self):
        for line in self:
            engineering_coefficient = line.product_id.engineering_coefficient
            if engineering_coefficient <= 0:
                engineering_coefficient = 1
            line.stock_quantity = line.engineering_quantity / engineering_coefficient

    # 生产损耗
    production_loss = fields.Float(string='Production loss')
    # 报价损耗
    quote_loss = fields.Float(string='Quotation loss')
    color_production_quantity = fields.Float(string='Production volume', compute='_compute_color_production_quantity')

    @api.depends('engineering_quantity', 'production_loss')
    def _compute_color_production_quantity(self):
        for line in self:
            line.color_production_quantity = line.engineering_quantity * (1 + line.production_loss)

    # 报价用量
    quote_quantity = fields.Float(string='Quoted dosage', compute='_compute_quote_quantity')

    @api.depends('color_production_quantity', 'quote_loss')
    def _compute_quote_quantity(self):
        for line in self:
            line.quote_quantity = line.stock_quantity * (1 + line.quote_loss)
    # 参考进价
    reference_price = fields.Float(string='Reference purchase price', related='product_id.reference_price')
    # 参考售价
    reference_sale_price = fields.Float(string='Reference selling price', related='product_id.reference_sale_price')
    # 成本价
    cost_price = fields.Float(string='Cost price', related='product_id.cost_price')
    # 报价单价
    quote_price = fields.Float(string='Quoted unit price')
    # 报价金额
    quote_amount = fields.Float(string='Quoted amount', compute='_compute_quote_amount')
    bom_id = fields.Many2one(required=False)

    @api.depends('quote_price', 'quote_quantity')
    def _compute_quote_amount(self):
        for line in self:
            line.quote_amount = line.quote_price * line.quote_quantity


class IdbMrpBomColor(models.Model):
    _inherit = 'idb.mrp.bom.color'

    matching_color_bom_id = fields.Many2one('matching.color.bom', string='Color matching BOM')

    # @profile
    def _create_matching_color_bom_line(self, matching_color_bom_line, bom_line, accessory_color_data, is_hardware=False):
        for line in bom_line:
            if is_hardware:
                engineering_quantity = line.product_qty
                stock_quantity = line.product_qty
            else:
                engineering_quantity = line.single_use * (1 + line.product_id.production_loss) * line.product_qty
                engineering_coefficient = line.product_id.engineering_coefficient
                # 库存单位用量
                if engineering_coefficient <= 0:
                    stock_quantity = engineering_quantity
                else:
                    stock_quantity = engineering_quantity / engineering_coefficient
            new_product_name = line.product_id.name + '-' + accessory_color_data[line.accessory_id.id]['color_name']
            # sql检查产品是否存在
            # sql = """
            # SELECT pp.id
            # FROM product_product pp
            # WHERE pp.id = (SELECT pt.id FROM product_template pt WHERE pt.name->>'value' = '{}' LIMIT 1);
            # """.format(new_product_name)
            # self.env.cr.execute(sql)
            # new_product_id = self.env.cr.fetchone()
            color_id = accessory_color_data[line.accessory_id.id]['color_id']
            new_product_id = self.env['product.product'].search([('name', '=', new_product_name)], limit=1)
            if not new_product_id:
                new_product_id = line.product_id.copy()
                new_product_id.write({'name': new_product_name, 'color_id': color_id, 'material_type': 'materials'})
            # else:
            #     new_product_id = self.env['product.product'].browse(new_product_id[0])
            if new_product_id.id in matching_color_bom_line:
                matching_color_bom_line[new_product_id.id]['engineering_quantity'] += engineering_quantity
                matching_color_bom_line[new_product_id.id]['stock_quantity'] += stock_quantity
            else:
                matching_color_bom_line[line.product_id.id] = {
                    'accessory_id': line.accessory_id.id,
                    'product_id': new_product_id.id,
                    'engineering_quantity': engineering_quantity,
                    'stock_quantity': stock_quantity,
                    'production_loss': line.product_id.production_loss,
                    'quote_loss': line.product_id.quote_loss,
                    'quote_price': line.product_id.reference_sale_price,
                    'color_id': color_id,
                    'specification': line.specification,
                }

    # @profile
    def update_matching_color_bom(self):
        accessory_color_data = {line.accessory_id.id: {'color_name': line.color_id.name, 'color_id': line.color_id.id} for line in self.color_line_ids}

        new_product_name = self.bom_id.product_tmpl_id.name + '-' + self.main_color_id.name
        # 查询产品是否存在
        color_product_tmpl_id = self.env['product.template'].search([('name', '=', new_product_name)], limit=1)
        if not color_product_tmpl_id:
            # 生成颜色主色产品
            color_product_tmpl_id = self.bom_id.product_tmpl_id.copy()
            color_product_tmpl_id.write({'name': new_product_name, 'color_id': self.color_id.id, 'material_type': 'materials'})
        # 根据BOM明细按产品分组，合并数量
        matching_color_bom_line = {}
        self._create_matching_color_bom_line(matching_color_bom_line, self.bom_id.bom_line_ids, accessory_color_data)
        self._create_matching_color_bom_line(matching_color_bom_line, self.bom_id.no_bom_line_ids, accessory_color_data, True)
        color_bom_line_ids = [(0, 0, line) for line in matching_color_bom_line.values()]
        matching_color_bom_id = self.matching_color_bom_id.create({
            'product_tmpl_id': color_product_tmpl_id.id,
            'main_color_id': self.main_color_id.id,
            'customer_id': self.bom_id.customer_id.id,
            'customer_number': self.bom_id.customer_number,
            'category_id': self.bom_id.category_id.id,
            'material_id': self.bom_id.material_id,
            'grid_number': self.bom_id.grid_number,
            'factory_number': self.bom_id.factory_number,
            'factory_version': self.bom_id.factory_version,
            'match_color_id': self.color_id.id,
            'color_bom_line_ids': color_bom_line_ids,
        })
        self.matching_color_bom_id = matching_color_bom_id.id