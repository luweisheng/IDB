# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


# idb.color.configuration.bom
class IdbColorConfigurationBom(models.Model):
    _name = 'idb.color.configuration.bom'
    _description = 'Color BOM configuration'

    name = fields.Char(string='name', default='Color BOM configuration', translate=True)
    bom_id = fields.Many2one('mrp.bom', string='BOM')
    table = fields.Html(string='Color table')
