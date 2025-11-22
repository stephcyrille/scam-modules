# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ParcelProductLine(models.Model):
    _name = 'parcel.product.line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = _('Parcel Product Line')
    _rec_name = 'product_id'
    _order = 'product_id'

    product_id = fields.Many2one("product.product", string=_("Article"), ondelete='cascade', tracking=True, required=True)
    quantity = fields.Integer(string=_("Quantity"), default=1, tracking=True)
    weight = fields.Float(string=_("Weight (in Kg)"), default=0, tracking=True, readonly=True, compute='_compute_weight')
    volume = fields.Float(string=_("Volume (in cm³)"), default=0, tracking=True, readonly=True, compute='_compute_volume')
    parcel_id = fields.Many2one("parcel.expedition", ondelete='cascade', tracking=True)
    
    def _compute_weight(self):
        for rec in self:
            weight = 0
            for line in rec.product_id:
                weight += (line.weight * rec.quantity) or 0.0
            rec.weight = weight

    def _compute_volume(self):
        for rec in self:
            volume = 0
            for line in rec.product_id:
                volume += (line.volume * rec.quantity) or 0.0
            rec.volume = volume