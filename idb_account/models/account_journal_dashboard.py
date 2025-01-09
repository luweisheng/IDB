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

    @api.onchange('file')
    def _onchange_file(self):
        file_content = self.file
        if file_content:
            # Decode the file content
            file_data = base64.b64decode(file_content)
            workbook = xlrd.open_workbook(file_contents=file_data)
            sheet = workbook.sheet_by_index(0)
            row_1 = sheet.row(1)
            partner_name = row_1[7].value
            partner_id = self.env['res.partner'].search([('name', '=', partner_name)], limit=1)
            invoice_payment_term = row_1[11].value
            # 付款条款
            invoice_payment_term_id = self.env['account.payment.term'].search([('name', '=', invoice_payment_term)],
                                                                              limit=1)
            if invoice_payment_term_id:
                invoice_payment_term_id = invoice_payment_term_id
            else:
                invoice_payment_term_id = self.env['account.payment.term'].create({'name': invoice_payment_term})
            if partner_id:
                partner_id = partner_id
            else:
                partner_id = self.env['res.partner'].create({
                    'name': partner_name,
                    'is_company': True,
                    'customer_rank': 1,
                })
                # 出仓单号
            stock_out_no = row_1[1].value
            name = partner_name + stock_out_no
            currency_name = row_1[9].value
            currency_id = self.env['res.currency'].search([('name', '=', currency_name)], limit=1).id
            original_amount = 0
            exchange_rate = float(row_1[10].value)
            document_date = row_1[2].value
            due_date = datetime.strptime(document_date, '%Y-%m-%d') + timedelta(days=invoice_payment_term_id.due_days)
            account_move = {
                'name': name,
                'stock_out_no': stock_out_no,
                'partner_id': partner_id,
                'currency_id': currency_id,
                'original_amount': 0,
                'exchange_rate': exchange_rate,
                'invoice_payment_term_id': invoice_payment_term_id.id,
                'document_date': document_date,
                'due_date': due_date,
                'invoice_line_ids': [(0, 0, {
                    'name': name,
                    'account_id': partner_id.property_account_receivable_id.id,
                    'currency_id': currency_id,
                    'exchange_rate': exchange_rate,
                    'original_amount': 0,
                    'debit': 0,
                }),
                     (0, 0, {
                         'name': name,
                         'account_id': self.env['account.account'].search([('code', 'ilike', '6001')], limit=1).id,
                         'credit': 0,
                     }),
                                     ],
            }
            # 循环遍历sheet数据，直到出现空行
            for row_idx in range(1, sheet.nrows):
                row = sheet.row(row_idx)
                # 价税合计数
                total_value_tax = row[31].value
                original_amount += total_value_tax
            account_move['original_amount'] = original_amount
            account_move['invoice_line_ids'][0][2]['original_amount'] = original_amount
            amount_currency = original_amount * exchange_rate
            account_move['invoice_line_ids'][0][2]['debit'] = amount_currency
            account_move['invoice_line_ids'][1][2]['credit'] = amount_currency
            self.update(account_move)

    # 客户
    partner_id = fields.Many2one('res.partner', string='Customer')
    # 单号
    stock_out_no = fields.Char(string='Stock Out No')
    # 付款条款
    invoice_payment_term_id = fields.Many2one('account.payment.term', string='Payment Term')
    # 币种
    currency_id = fields.Many2one('res.currency', string='Currency')
    # 汇率
    exchange_rate = fields.Float(string='Exchange Rate')

    @api.onchange('exchange_rate', 'original_amount')
    def _onchange_exchange_rate(self):
        if self.exchange_rate and self.original_amount:
            for line in self.invoice_line_ids:
                if line.currency_id:
                    line.debit = self.original_amount * self.exchange_rate
                    line.exchange_rate = self.exchange_rate
                else:
                    line.credit = self.original_amount * self.exchange_rate
    # 原始金额
    original_amount = fields.Float(string='Original Amount')
    # 单据日期
    document_date = fields.Date(string='Document Date')

    # 会计凭证
    invoice_line_ids = fields.One2many('idb.account.upload.move.line', 'account_move_id', string='Invoice Line')

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
        # 跳转会计凭证试图
        return {
            'type': 'ir.actions.act_window',
            'name': _('Account Move'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': account_move.id,
        }

    def action_generate_voucher_sale(self):
        exchange_rate = self.exchange_rate
        original_amount = self.original_amount
        currency_id = self.currency_id.id
        stock_out_no = self.stock_out_no
        name = self.name
        account_move = {
            'move_type': 'out_invoice',
            'invoice_date': self.document_date,
            'stock_picking_name': stock_out_no,
            'partner_id': self.partner_id.id,
            'currency_id': currency_id,
            'original_amount': original_amount,
            'exchange_rate': exchange_rate,
            'invoice_payment_term_id': self.invoice_payment_term_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': name,
                'abstract': name,
                'stock_picking_name': stock_out_no,
                'currency_id': currency_id,
                'quantity': 1,
                'price_unit': original_amount * exchange_rate
            })],
        }
        # 创建凭证
        account_move = self.env['account.move'].create(account_move)
        # 跳转会计凭证试图
        return {
            'type': 'ir.actions.act_window',
            'name': _('Account Move'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': account_move.id,
        }

    # 生成凭证
    def action_generate_voucher(self):
        account_type = self.env.context.get('type')
        if account_type == 'in_invoice':
            return self.action_generate_voucher_purchase()
        elif account_type == 'out_invoice':
            return self.action_generate_voucher_sale()


class IdbAccountUploadMoveLine(models.TransientModel):
    _name = "idb.account.upload.move.line"
    _description = "IDB Account Upload Move Line"

    account_move_id = fields.Many2one('idb.account.upload', string='Account Move')
    name = fields.Char(string='abstract')
    # 会计科目
    account_id = fields.Many2one('account.account', string='Account')
    # 借方
    debit = fields.Float(string='Debit')
    # 贷方
    credit = fields.Float(string='Credit')
    # 原币金额
    original_amount = fields.Float(string='Amount Currency')
    # 汇率
    exchange_rate = fields.Float(string='Exchange Rate')
    # 币别
    currency_id = fields.Many2one('res.currency', string='Currency')

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
