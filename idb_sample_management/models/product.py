# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_view_sample_order(self):
        self.product_tmpl_id.action_view_sample_order()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sample_order_count = fields.Integer(compute='_compute_sample_order_count', string='Sample order quantity')

    def _compute_sample_order_count(self):
        for record in self:
            record.sample_order_count = self.env['idb.sample.management'].search_count([('bom_id.product_id.product_tmpl_id', '=', record.id)])

    def action_view_sample_order(self):
        action = self.env.ref('idb_sample_management.action_sample_management_order').read()[0]
        action['domain'] = [('bom_id.product_id.product_tmpl_id', '=', self.id)]
        return action