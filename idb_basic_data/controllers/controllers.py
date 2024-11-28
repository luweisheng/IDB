# -*- coding: utf-8 -*-
# from odoo import http


# class IdbBasicData(http.Controller):
#     @http.route('/idb_basic_data/idb_basic_data', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/idb_basic_data/idb_basic_data/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('idb_basic_data.listing', {
#             'root': '/idb_basic_data/idb_basic_data',
#             'objects': http.request.env['idb_basic_data.idb_basic_data'].search([]),
#         })

#     @http.route('/idb_basic_data/idb_basic_data/objects/<model("idb_basic_data.idb_basic_data"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('idb_basic_data.object', {
#             'object': obj
#         })

