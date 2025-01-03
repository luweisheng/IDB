# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sample_management_id = fields.Many2one('sample.management', string='Sample management')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    sample_management_line_id = fields.Many2one('mrp.eco.line', string='Sample management')