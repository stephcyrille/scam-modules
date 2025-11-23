# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ParcelServiceLine(models.Model):
    _name = 'parcel.service.line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = _('Parcel Services fees Line')
    _rec_name = 'product_id'
    _order = 'product_id'

    product_id = fields.Many2one("product.product", string=_("Service"), ondelete='cascade', tracking=True, required=True)
    product_uom_qty = fields.Float(string=_("Quantity"), default=1, tracking=True)
    price_unit = fields.Float(string=_("Unit price"), default=0, tracking=True, readonly=True, 
                              store=True, compute='_compute_unit_price')
    parcel_id = fields.Many2one("parcel.expedition", ondelete='cascade', tracking=True)
    
    @api.depends('product_id', 'product_uom_qty')
    def _compute_unit_price(self):
        for rec in self:
            price = 0
            if rec.product_id:
                price = (rec.product_id.list_price * rec.product_uom_qty) or 0.0
            rec.price_unit = price