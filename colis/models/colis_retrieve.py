# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ColisRetrieve(models.Model):
    _name = 'colis.retrieve'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Retrait de colis'
    _rec_name = 'ref'

    ref = fields.Char('Référence', required=True, tracking=True, index=True, copy=False, default="New", readonly=True)
    sender_id = fields.Many2one("res.partner", string="Expéditeur", tracking=True, compute='_compute_sender_id')
    receiver_id = fields.Many2one("res.partner", string="Destinataire", tracking=True, required=True)
    reception_id = fields.Many2one("colis.reception", string="Colis", tracking=True, required=True,
                                   domain=[('state', '=', 'stocked')])
    travel_no_id = fields.Many2one("colis.travel", string="N° de voyage", tracking=True, compute='_compute_travel_no',
                                   store=True, readonly=True)
    place_id = fields.Many2one("stock.location", string="Emplacement", tracking=True, readonly=True, store=True,
                               compute='_compute_place_id')
    date = fields.Date("Date de retrait", tracking=True, default=fields.Date.today(), readonly=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Confirmé'),
        ('terminate', 'Terminé')], string='Status',
        copy=False, default='draft', index=True, readonly=True, tracking=True)
    colis_products_ids = fields.One2many('colis.product.line', 'retrieve_id', store=True, tracking=True,
                                         compute='_compute_products_items')

    @api.depends('reception_id')
    def _compute_sender_id(self):
        for reception in self:
            if reception.reception_id.sender_id:
                reception.sender_id = reception.reception_id.sender_id
            else:
                reception.sender_id = False

    @api.depends('reception_id')
    def _compute_travel_no(self):
        for retrieve in self:
            if retrieve.reception_id.expedition_id.travel_no:
                retrieve.travel_no_id = retrieve.reception_id.expedition_id.travel_no
            else:
                retrieve.travel_no_id = False

    @api.depends('reception_id')
    def _compute_place_id(self):
        for retrieve in self:
            if retrieve.reception_id.place_id:
                retrieve.place_id = retrieve.reception_id.place_id
            else:
                retrieve.place_id = False

    @api.depends('reception_id')
    def _compute_products_items(self):
        for retrieve in self:
            if retrieve.reception_id.expedition_id.colis_product_ids:
                retrieve.colis_products_ids = retrieve.reception_id.expedition_id.colis_product_ids
            else:
                retrieve.colis_products_ids = False