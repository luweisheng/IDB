# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class MrpBomNoPartDetail(models.TransientModel):
    _name = 'mrp.bom.no.part.detail'


class MrpBomPartDetail(models.TransientModel):
    _name = 'mrp.bom.part.detail'


# idb.product.quote.line
class IdbProductQuoteLine(models.TransientModel):
    _name = 'idb.product.quote.line'


# idb.product.no.position.line
class IdbProductNoPositionLine(models.TransientModel):
    _name = 'idb.product.no.position.line'


# idb.product.position.line
class IdbProductPositionLine(models.TransientModel):
    _name = 'idb.product.position.line'


# idb.product.bom
class IdbProductBom(models.Model):
    _name = 'idb.product.bom'


class IdbSampleManagement(models.Model):
    _inherit = 'idb.sample.management'

    bom_count = fields.Integer(string='Bom quantity', compute='_compute_bom_count')

    @api.model
    def _compute_bom_count(self):
        for record in self:
            record.bom_count = self.env['mrp.bom'].search_count([('sample_id', '=', record.id)])

    def action_open_mrp_bom_view(self):
        self.ensure_one()
        return {
            'name': _('Bom'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'mrp.bom',
            'domain': [('sample_id', '=', self.id)],
            'context': {'default_sample_id': self.id},
            'target': 'current',
        }


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    sample_id = fields.Many2one('idb.sample.management', string='Sample list', track_visibility='onchange')
