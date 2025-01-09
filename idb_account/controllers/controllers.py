# -*- coding: utf-8 -*-
# from odoo import http


# class IdbAccount(http.Controller):
#     @http.route('/idb_account/idb_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/idb_account/idb_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('idb_account.listing', {
#             'root': '/idb_account/idb_account',
#             'objects': http.request.env['idb_account.idb_account'].search([]),
#         })

#     @http.route('/idb_account/idb_account/objects/<model("idb_account.idb_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('idb_account.object', {
#             'object': obj
#         })

