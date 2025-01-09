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


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # 库存单号
    stock_picking_name = fields.Char(string='Warehouse Bill Number')
    abstract = fields.Char(string='Abstract')