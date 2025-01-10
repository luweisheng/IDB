# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    # 到期天数
    due_days = fields.Integer(string='Due Days')


class AccountMove(models.Model):
    _inherit = 'account.move'

    # 库存单号
    stock_picking_name = fields.Char(string='Warehouse Bill Number')
    # 汇率
    exchange_rate = fields.Float(string='Exchange Rate')
    # 原始金额
    original_amount = fields.Float(string='Original Amount')
    abstract = fields.Char(string='Abstract')

    # 导入数据明细
    gt_stock_move_ids = fields.One2many('idb.account.move.line', 'move_id', string='Import Data Details')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # 库存单号
    stock_picking_name = fields.Char(string='Warehouse Bill Number')
    abstract = fields.Char(string='Abstract', related='move_id.abstract')


class IdbAccountMoveLine(models.Model):
    _name = "idb.account.move.line"
    _description = "IDB Account Upload Move Line"

    move_id = fields.Many2one('account.move', string='Account Move')
    name = fields.Char(string='Abstract')
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