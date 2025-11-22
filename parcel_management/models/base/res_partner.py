# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    parcel_city_id = fields.Many2one(
        'parcel.city', string=_("City"),
        help=_("City of the partner, used for parcel management"),
        tracking=True
    )

    @api.onchange('parcel_city_id')
    def _onchange_parcel_city_id(self):
        """ Update the city field when parcel_city_id is changed """
        if self.parcel_city_id:
            self.city = self.parcel_city_id.name
            self.state_id = self.parcel_city_id.state_id
            self.country_id = self.parcel_city_id.country_id
        else:
            self.city = ''
            self.state_id = False
            self.country_id = False

    def write(self, vals):
        """ Override write to ensure city, state, and country are updated """
        if 'parcel_city_id' in vals:
            city_rec = self.env['parcel.city'].browse(vals['parcel_city_id'])
            if city_rec:
                self.city = city_rec.name
        return super(ResPartner, self).write(vals)