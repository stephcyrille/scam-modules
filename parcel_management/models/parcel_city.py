# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ParcelCity(models.Model):
    _name = 'parcel.city'
    _description = _('City')
    _rec_name = 'name'
    _order = 'name'
    _sql_constraints = [
        ('name_uniq', 'unique(name, country_id, state_id)', _('The city name must be unique per country and state.'))
    ]

    country_id = fields.Many2one("res.country", string=_("Country"), required=True)
    state_id = fields.Many2one("res.country.state", string=_("State"), required=True)
    name = fields.Char(_('Name'), required=True)