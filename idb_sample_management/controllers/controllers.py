# -*- coding: utf-8 -*-
# from odoo import http


# class IdbSampleManagement(http.Controller):
#     @http.route('/idb_sample_management/idb_sample_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/idb_sample_management/idb_sample_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('idb_sample_management.listing', {
#             'root': '/idb_sample_management/idb_sample_management',
#             'objects': http.request.env['idb_sample_management.idb_sample_management'].search([]),
#         })

#     @http.route('/idb_sample_management/idb_sample_management/objects/<model("idb_sample_management.idb_sample_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('idb_sample_management.object', {
#             'object': obj
#         })

