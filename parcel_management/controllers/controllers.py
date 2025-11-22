# -*- coding: utf-8 -*-
# from odoo import http


# class ParcelManagement(http.Controller):
#     @http.route('/parcel_management/parcel_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/parcel_management/parcel_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('parcel_management.listing', {
#             'root': '/parcel_management/parcel_management',
#             'objects': http.request.env['parcel_management.parcel_management'].search([]),
#         })

#     @http.route('/parcel_management/parcel_management/objects/<model("parcel_management.parcel_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('parcel_management.object', {
#             'object': obj
#         })

