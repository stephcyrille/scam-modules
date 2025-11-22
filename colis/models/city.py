# -*- coding: utf-8 -*-

from odoo import models, fields, api


class colis(models.Model):
    _name = 'colis.city'
    _description = 'Villes'
    _rec_name = 'name'

    country_id = fields.Many2one("res.country", string="Pays", required=True)
    state_id = fields.Many2one("res.country.state", string="Région", required=True)
    name = fields.Char('Nom')
