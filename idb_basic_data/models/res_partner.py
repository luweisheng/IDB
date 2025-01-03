# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    barcode = fields.Char(string='Client number', translate=True)

    @api.model
    def create(self, vals):
        result = super(ResPartner, self).create(vals)
        supplier_rank = self.env.context.get('supplier_rank')
        if supplier_rank:
            result.write({'supplier_rank': supplier_rank})
        return result