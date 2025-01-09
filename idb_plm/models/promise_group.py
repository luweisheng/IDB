# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    order_template_id = fields.Many2one('sample.development.single.template', string='Order template')
    # 出格组长
    cg_user_id = fields.Many2one('res.users', string='CG Leader')