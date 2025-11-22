# -*- coding: utf-8 -*-
# from odoo import http


# class Colis(http.Controller):
#     @http.route('/colis/colis/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/colis/colis/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('colis.listing', {
#             'root': '/colis/colis',
#             'objects': http.request.env['colis.colis'].search([]),
#         })

#     @http.route('/colis/colis/objects/<model("colis.colis"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('colis.object', {
#             'object': obj
#         })
