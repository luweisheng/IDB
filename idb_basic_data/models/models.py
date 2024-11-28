# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class idb_basic_data(models.Model):
#     _name = 'idb_basic_data.idb_basic_data'
#     _description = 'idb_basic_data.idb_basic_data'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

