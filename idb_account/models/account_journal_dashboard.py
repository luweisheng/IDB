# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
import base64
import xlrd

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IdbAccountUpload(models.TransientModel):
    _name = "idb.account.upload"
    _description = "IDB Account Upload"

    name = fields.Char(string='Name')
    file = fields.Binary(string='File')

    # 应付日期
    due_date = fields.Date(string='Due Date')

    # 借方科目
    debit_account_id = fields.Many2one('account.account', string='Debit Account')
    # 贷方科目
    credit_account_id = fields.Many2one('account.account', string='Credit Account')

    # 汇总会计明细
    account_move_ids = fields.One2many('idb.account.collect.move.line', 'account_move_id', string='Account Move')

    # 合计金额
    total_amount = fields.Float(string='Total Amount')

    @api.onchange('file')
    def _onchange_file(self):
        file_content = self.file
        if file_content:
            # Decode the file content
            file_data = base64.b64decode(file_content)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_index(0)
            total_amount = 0
            # 按照出仓单号分组
            account_move = {}
            # 循环遍历sheet数据，直到出现空行
            for row_idx in range(1, sheet.nrows):
                row = sheet.row(row_idx)
                # 出仓单号
                stock_out_no = row[1].value
                # 出仓日期
                document_date = row[2].value
                # 订货日期
                order_date = row[3].value
                # 交货日期
                delivery_date = row[4].value
                # 客户
                partner_name = row[7].value
                partner_id = self.env['res.partner'].search([('name', '=', partner_name)], limit=1)
                if partner_id:
                    partner_id = partner_id
                else:
                    partner_id = self.env['res.partner'].create({
                        'name': partner_name,
                        'is_company': True,
                        'customer_rank': 1,
                    })
                # 出仓员
                user_name = row[8].value
                # 币种
                currency_name = row[9].value
                currency_id = self.env['res.currency'].search([('name', '=', currency_name)], limit=1)
                if not currency_id:
                    raise UserError(_("Coins %s do not exist, please contact the administrator to maintain the data" % currency_name))
                # 汇率
                exchange_rate = float(row[10].value)
                # 结算方式
                invoice_payment_term = row[11].value
                # 付款条款
                invoice_payment_term_id = self.env['account.payment.term'].search([('name', '=', invoice_payment_term)],
                                                                                  limit=1)
                if invoice_payment_term_id:
                    invoice_payment_term_id = invoice_payment_term_id
                else:
                    invoice_payment_term_id = self.env['account.payment.term'].create({'name': invoice_payment_term})
                # 订单号
                order_no = row[17].value
                # 款号
                style_no = row[18].value
                # 物料名称
                material_name = row[20].value
                # 物料分类
                material_category = row[24].value
                # 数量
                quantity = float(row[27].value)
                # 单位
                unit = row[28].value
                # 单价
                price_unit = float(row[29].value)
                # 价税合计
                line_total_value_tax = float(row[31].value)
                name = partner_name + stock_out_no
                line = (0, 0, {
                    'name': name,
                    'stock_out_no': stock_out_no,
                    'order_date': order_date,
                    'delivery_date': delivery_date,
                    'document_date': document_date,
                    'partner_id': partner_id.id,
                    'user_name': user_name,
                    'currency_id': currency_id,
                    'exchange_rate': exchange_rate,
                    'invoice_payment_term_id': invoice_payment_term_id.id,
                    'order_no': order_no,
                    'style_no': style_no,
                    'material_name': material_name,
                    'material_category': material_category,
                    'quantity': quantity,
                    'unit': unit,
                    'price_unit': price_unit,
                    'total_value_tax': line_total_value_tax,
                })
                if stock_out_no not in account_move:
                    account_move[stock_out_no] = {
                        'name': name,
                        'stock_out_no': stock_out_no,
                        'document_date': document_date,
                        'partner_id': partner_id.id,
                        'user_name': user_name,
                        'currency_id': currency_id,
                        'exchange_rate': exchange_rate,
                        'invoice_payment_term_id': invoice_payment_term_id.id,
                        'total_value_tax': line_total_value_tax,
                        'invoice_line_ids': [line]
                    }
                else:
                    account_move[stock_out_no]['invoice_line_ids'].append(line)
                    account_move[stock_out_no]['total_value_tax'] += line_total_value_tax
                total_amount += line_total_value_tax * exchange_rate
            account_data = {
                'debit_account_id': self.env['account.account'].search([('code', 'ilike', '1122')], limit=1).id,
                'credit_account_id': self.env['account.account'].search([('code', 'ilike', '6001')], limit=1).id,
                'total_amount': total_amount,
                'account_move_ids': [(0, 0, account_line) for account_line in account_move.values()]
            }
            self.update(account_data)
            return

    def action_generate_voucher_purchase(self):
        # 解析文件数据
        file_content = self.file
        if not file_content:
            raise UserError(_("Please upload ET file"))
        # Decode the file content
        file_data = base64.b64decode(file_content)
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)
        partner_name = sheet.row(1)[7].value
        partner_id = self.env['res.partner'].search([('name', '=', partner_name)], limit=1)
        if partner_id:
            partner_id = partner_id.id
        else:
            partner_id = self.env['res.partner'].create({
                'name': partner_name,
                'is_company': True,
                'supplier_rank': 1,
            }).id
        account_move = {
            'move_type': 'in_invoice',
            'partner_id': partner_id,
            'invoice_line_ids': [],
        }
        # 循环遍历sheet数据，直到出现空行
        for row_idx in range(1, sheet.nrows):
            row = sheet.row(row_idx)
            account_move['invoice_line_ids'].append((0, 0, {
                'name': row[20].value,
                'quantity': row[28].value,
                'price_unit': row[31].value
            }))
        # 创建凭证
        account_move = self.env['account.move'].create(account_move)
        # 跳转会计凭证视图
        return {
            'type': 'ir.actions.act_window',
            'name': _('Account Move'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': account_move.id,
        }

    def action_generate_voucher_sale(self):
        account_move_data = []
        for line in self.account_move_ids:
            exchange_rate = line.exchange_rate
            original_amount = line.total_value_tax
            currency_id = line.currency_id.id
            stock_out_no = line.stock_out_no
            name = line.name
            account_move = {
                'abstract': name,
                'move_type': 'out_invoice',
                'invoice_date': line.document_date,
                'stock_picking_name': stock_out_no,
                'partner_id': line.partner_id.id,
                'currency_id': currency_id,
                'original_amount': original_amount,
                'exchange_rate': exchange_rate,
                'invoice_payment_term_id': line.invoice_payment_term_id.id,
                'invoice_line_ids': [(0, 0, {
                    'name': name,
                    'stock_picking_name': stock_out_no,
                    'currency_id': currency_id,
                    'quantity': 1,
                    'price_unit': line.total_amount,
                })],
                'gt_stock_move_ids': [(0, 0, {
                    'name': name,
                    'stock_out_no': stock_out_no,
                    'order_date': stock_move_id.order_date,
                    'delivery_date': stock_move_id.delivery_date,
                    'document_date': stock_move_id.document_date,
                    'partner_id': stock_move_id.partner_id.id,
                    'user_name': stock_move_id.user_name,
                    'currency_id': currency_id,
                    'exchange_rate': exchange_rate,
                    'invoice_payment_term_id': stock_move_id.invoice_payment_term_id.id,
                    'order_no': stock_move_id.order_no,
                    'style_no': stock_move_id.style_no,
                    'material_name': stock_move_id.material_name,
                    'material_category': stock_move_id.material_category,
                    'quantity': stock_move_id.quantity,
                    'unit': stock_move_id.unit,
                    'price_unit': stock_move_id.price_unit,
                    'total_value_tax': stock_move_id.total_value_tax,
                }) for stock_move_id in line.invoice_line_ids],
            }
            account_move_data.append(account_move)
        account_move_ids = self.env['account.move'].create(account_move_data)
        # 跳转会计凭证试图
        return {
            'type': 'ir.actions.act_window',
            'name': _('Account Move'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', account_move_ids.ids)],
        }

    # 生成凭证
    def action_generate_voucher(self):
        account_type = self.env.context.get('account_type')
        if account_type == 'in_invoice':
            return self.action_generate_voucher_purchase()
        elif account_type == 'out_invoice':
            return self.action_generate_voucher_sale()


class IdbAccountCollectMoveLine(models.TransientModel):
    _name = "idb.account.collect.move.line"
    _description = "IDB Account Upload Move Line"

    name = fields.Char(string='Abstract')
    account_move_id = fields.Many2one('idb.account.upload', string='Account Move')
    # 出仓单号
    stock_out_no = fields.Char(string='The warehouse receipt number')
    # 出仓日期
    document_date = fields.Date(string='Exit date')
    # 客户
    partner_id = fields.Many2one('res.partner', string='Customer')
    # 出仓员
    user_name = fields.Char(string='Warehouse staff')
    # 币种
    currency_id = fields.Many2one('res.currency', string='Currency')
    # 汇率
    exchange_rate = fields.Float(string='Exchange Rate')

    @api.onchange('exchange_rate')
    def _onchange_exchange_rate(self):
        for record in self:
            record.invoice_line_ids.exchange_rate = record.exchange_rate

    # 付款条款
    invoice_payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')

    @api.onchange('invoice_payment_term_id')
    def _onchange_invoice_payment_term_id(self):
        for record in self:
            record.invoice_line_ids.invoice_payment_term_id = record.invoice_payment_term_id.id

    # 摘要
    abstract = fields.Char(string='Abstract')
    # 价税合计
    total_value_tax = fields.Float(string='Total value-added tax')
    # 总金额
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount')

    @api.depends('total_value_tax', 'exchange_rate')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.total_value_tax * record.exchange_rate

    invoice_line_ids = fields.One2many('idb.account.upload.move.line', 'account_move_id', string='Billing summary')


class IdbAccountUploadMoveLine(models.TransientModel):
    _name = "idb.account.upload.move.line"
    _description = "IDB Account Upload Move Line"

    name = fields.Char(string='Abstract')
    account_move_id = fields.Many2one('idb.account.collect.move.line', string='Account Move')
    stock_out_no = fields.Char(string='The warehouse receipt number')
    document_date = fields.Date(string='Exit date')
    order_date = fields.Date(string='Order date')
    delivery_date = fields.Date(string='Delivery date')
    partner_id = fields.Many2one('res.partner', string='Customer')
    user_name = fields.Char(string='Warehouse staff')
    currency_id = fields.Many2one('res.currency', string='Currency')
    exchange_rate = fields.Float(string='Exchange Rate')
    order_no = fields.Char(string='Order number')
    style_no = fields.Char(string='Style number')
    material_name = fields.Char(string='Material name')
    material_category = fields.Char(string='Material category')
    quantity = fields.Float(string='Quantity')
    unit = fields.Char(string='Unit')
    price_unit = fields.Float(string='Unit price')
    total_value_tax = fields.Float(string='Total value-added tax')
    # 付款条款
    invoice_payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def action_create_vendor_bill(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inventory Documents Generate Vouchers'),
            'res_model': 'idb.account.upload',
            'view_mode': 'form',
            'context': {'type': 'in_invoice'},
            'target': 'new',
        }

    def action_create_sale_account_move(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Inventory Documents Generate Vouchers'),
            'res_model': 'idb.account.upload',
            'view_mode': 'form',
            'context': {'type': 'out_invoice'},
            'target': 'new',
        }
