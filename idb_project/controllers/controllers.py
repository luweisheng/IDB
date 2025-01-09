# -*- coding: utf-8 -*-
# from odoo import http


# class IdbProject(http.Controller):
#     @http.route('/idb_project/idb_project', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/idb_project/idb_project/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('idb_project.listing', {
#             'root': '/idb_project/idb_project',
#             'objects': http.request.env['idb_project.idb_project'].search([]),
#         })

#     @http.route('/idb_project/idb_project/objects/<model("idb_project.idb_project"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('idb_project.object', {
#             'object': obj
#         })

