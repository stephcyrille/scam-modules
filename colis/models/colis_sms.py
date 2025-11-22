# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ColisSms(models.Model):
    _name = 'colis.sms'
    _description = 'Short Messages Service'
    _rec_name = 'to_number'

    from_number = fields.Char('Expéditeur', required=True)
    to_number = fields.Char('Destinataire', required=True)
    message = fields.Text('Message', required=True)
    date = fields.Date("Date", default=fields.Date.today(), readonly=True)