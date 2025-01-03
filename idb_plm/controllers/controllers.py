# -*- coding: utf-8 -*-
# from odoo import http


# class IdbPlm(http.Controller):
#     @http.route('/idb_plm/idb_plm', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/idb_plm/idb_plm/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('idb_plm.listing', {
#             'root': '/idb_plm/idb_plm',
#             'objects': http.request.env['idb_plm.idb_plm'].search([]),
#         })

#     @http.route('/idb_plm/idb_plm/objects/<model("idb_plm.idb_plm"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('idb_plm.object', {
#             'object': obj
#         })

