# -*- coding: utf-8 -*-
# from odoo import http


# class ManufacturSale(http.Controller):
#     @http.route('/manufactur_sale/manufactur_sale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/manufactur_sale/manufactur_sale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('manufactur_sale.listing', {
#             'root': '/manufactur_sale/manufactur_sale',
#             'objects': http.request.env['manufactur_sale.manufactur_sale'].search([]),
#         })

#     @http.route('/manufactur_sale/manufactur_sale/objects/<model("manufactur_sale.manufactur_sale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('manufactur_sale.object', {
#             'object': obj
#         })
