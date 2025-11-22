# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests


def sendSMS(receiver, body, exp='ADEO Colis'):
    base_url = 'https://sms.etech-keys.com/ss/api.php'
    paswd = 'et9t459'
    login = '693458540'

    url = '%s?login=%s&password=%s&sender_id=%s&destinataire=%s&message=%s' % (
        base_url, login, paswd, exp, receiver, body)
    try:
        response = requests.request("GET", url, timeout=30)
        values = {
            "responseCode": response.status_code,
            "description": 'OK'
        }
    except Exception as e:
        values = {
            "responseCode": 500,
            "description": e.__str__(),
        }

    return values


class ColisReception(models.Model):
    _name = 'colis.reception'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Reception'
    _rec_name = 'ref'

    ref = fields.Char('Référence', required=True, tracking=True, index=True, copy=False, default="New", readonly=True)
    travel_no_id = fields.Many2one("colis.travel", string="N° de voyage", tracking=True, compute='_compute_travel_no',
                                   store=True, readonly=True)
    expedition_id = fields.Many2one("colis.expedition", string="Colis", tracking=True, required=True)
    place_id = fields.Many2one("stock.location", string="Emplacement", tracking=True, required=True)
    date = fields.Date("Date de reception", tracking=True, default=fields.Date.today(), readonly=True)
    company_branch_id = fields.Many2one("res.company.branch", string="Agence", tracking=True, required=True,
                                        help='Agence où se trouve le colis')
    colis_products_ids = fields.One2many('colis.product.line', 'reception_id', string='Objets',
                                         compute='_compute_products_items', store=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('received', 'Receptionné'),
        ('stocked', 'Rangé')], string='Status',
        copy=False, default='draft', index=True, readonly=True, tracking=True)
    sender_id = fields.Many2one("res.partner", string="Expéditeur", tracking=True, compute='_compute_sender_id',
                                store=True)
    receiver_id = fields.Many2one("res.partner", string="Destinataire", tracking=True, compute='_compute_receiver_id',
                                  store=True)

    @api.depends('expedition_id')
    def _compute_travel_no(self):
        for colis_recption in self:
            if colis_recption.expedition_id.travel_no:
                colis_recption.travel_no_id = colis_recption.expedition_id.travel_no
            else:
                colis_recption.travel_no_id = False

    @api.depends('expedition_id')
    def _compute_products_items(self):
        for colis_recption in self:
            # print("\n\n\nLAAAAAAAAAAAAAAAAAAAA %s\n\n" % related_recordsets)
            if colis_recption.expedition_id.colis_product_ids:
                colis_recption.colis_products_ids = colis_recption.expedition_id.colis_product_ids
            else:
                colis_recption.colis_products_ids = False

    @api.depends('expedition_id')
    def _compute_sender_id(self):
        for reception in self:
            if reception.expedition_id.sender_id:
                reception.sender_id = reception.expedition_id.sender_id
            else:
                reception.sender_id = False

    @api.depends('expedition_id')
    def _compute_receiver_id(self):
        for reception in self:
            if reception.expedition_id.receiver_id:
                reception.receiver_id = reception.expedition_id.receiver_id
            else:
                reception.receiver_id = False

    def set_draft_action(self):
        for rec in self:
            rec.write({
                'state': 'draft'
            })

    def set_received_action(self):
        for rec in self:
            if rec.place_id:
                rec.expedition_id.write({'state': 'arrived'})
                rec.write({'state': 'received'})
            else:
                raise ValidationError("Bien vouloir définir l'emplacement du colis")

    def set_stocked_action(self):
        for rec in self:
            rec.write({
                'ref': self.env['ir.sequence'].next_by_code("colis.reception") or 'New',
                'state': 'stocked'
            })

            body = '%s %s, votre colis est arrive a %s.\nBien vouloir vous raproché de notre agence dans la ville.'\
                   'La reference du colis est: %s.\n\nNous vous remercions pour votre confiance.' % \
                   (rec.expedition_id.receiver_id.title.name, rec.expedition_id.receiver_id.name,
                    rec.expedition_id.to_place_id.name, rec.ref)
            from_nber = 'Adeo Colis'
            response = sendSMS(rec.expedition_id.receiver_id.phone, body, from_nber)

            if response['responseCode'] == 200:
                msg = {
                    'from_number': from_nber,
                    'to_number': rec.expedition_id.receiver_id.phone,
                    'message': body,
                }

                self.env['colis.sms'].create(msg)
            else:
                raise ValidationError('Error due à la notification du client')
