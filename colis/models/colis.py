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


class ColisType(models.Model):
    _name = 'colis.type'
    _description = 'Types de colis'
    _rec_name = 'name'

    name = fields.Char('Nom', required=True)
    code = fields.Char('Code', required=True)


class ColisColis(models.Model):
    _name = 'colis.expedition'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Colis'
    _rec_name = 'ref'

    ref = fields.Char('Référence', required=True, tracking=True, index=True, copy=False, default="New", readonly=True)
    type_id = fields.Many2one("colis.type", string="Type de colis", tracking=True, required=True)
    sender_id = fields.Many2one("res.partner", string="Expéditeur", tracking=True, required=True)
    receiver_id = fields.Many2one("res.partner", string="Destinataire", tracking=True, required=True)
    driver_id = fields.Many2one("res.partner", string="Chauffeur", tracking=True)
    plate_no = fields.Char('Immatriculation', tracking=True, index=True)
    travel_no = fields.Many2one("colis.travel", string="N° du voyage", tracking=True)
    from_warehouse_id = fields.Many2one("stock.warehouse", string="Entrepôt d'origine", tracking=True, required=True,
                                        help='Lieu de stockage du colis avant expédition l\'agence')
    to_warehouse_id = fields.Many2one("stock.warehouse", string="Entrepôt arrivée", tracking=True,
                                      help='Correspond au lieu de stockage du colis arrivé à destination dans l\'agence')
    current_warehouse_id = fields.Many2one("stock.warehouse", string="Entrepôt actuel", tracking=True, required=True)
    current_location_id = fields.Many2one("stock.location", string="Emplacement actuel", tracking=True,
                                          help='Il s\'agit ici du lieu exacte où l\'élément se situe dans l\'entrepôt '
                                               'Lorsque l\'élément sera au statut envoyé, cette valeur sera nulle')
    operator_id = fields.Many2one("res.users", string="Opérateur", tracking=True, required=True,
                                  help='Opérateur de saisie de dolis, par défaut c\'est l\'utilisateur connecté qu\'on '
                                       'sélectionne', default=lambda self: self.env.user)
    from_place_id = fields.Many2one("colis.city", string="Ville départ", tracking=True, required=True,
                                    help='Ville de départ')
    to_place_id = fields.Many2one("colis.city", string="Ville arrivée", tracking=True, required=True,
                                  help='Ville de destination')
    weight = fields.Float("Poids (en Kg)", default=0, tracking=True, readonly=True, compute='_compute_total_weight')
    capacity = fields.Float("Volume (en m3)", default=0, tracking=True, readonly=True,
                            compute='_compute_total_capacity')
    price = fields.Float("Prix du service", default=0, tracking=True, readonly=True)
    currency_id = fields.Many2one(
        'res.currency', 'Currency', compute='_compute_currency_id')
    description = fields.Text()
    date = fields.Date("Date enregistrement", tracking=True, default=fields.Date.today(), readonly=True)
    departure_date = fields.Date("Date de départ", tracking=True, required=True)
    estimated_arrival_date = fields.Date("Date d'arrivée", tracking=True, required=True)
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('checked', 'Vérifié'),
        ('confirmed', 'Confirmé'),
        ('sent', 'Expédié'),
        ('canceled', 'Annulé'),
        ('arrived', 'Arrivé'),
        ('end', 'Retiré')], string='Status',
        copy=False, default='draft', index=True, readonly=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env['res.company']._get_main_company())
    company_branch_id = fields.Many2one("res.company.branch", string="Agence", tracking=True, required=True,
                                        help='Agence où se trouve le colis')
    colis_product_ids = fields.One2many('colis.product.line', 'colis_id', string='Articles', tracking=True)

    def _compute_total_weight(self):
        for rec in self:
            weight = 0
            for line in rec.colis_product_ids:
                weight += line.weight or 0.0
            rec.weight = weight

    def _compute_total_capacity(self):
        for rec in self:
            volume = 0
            for line in rec.colis_product_ids:
                volume += line.volume or 0.0
            rec.capacity = volume

    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        # print("\n\n\nMAIN COMPANY: %s\n\n" % main_company)
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    def set_draft_action(self):
        for rec in self:
            rec.write({
                'state': 'draft'
            })

    def check_action(self):
        for rec in self:
            if not rec.sender_id.phone or not rec.sender_id.mobile:
                raise ValidationError("Vous devez saisir au moins un numéro de téléphone de l'expéditeur")
            elif not rec.receiver_id.phone or not rec.receiver_id.mobile:
                raise ValidationError("Vous devez saisir au moins un numéro de téléphone du destinataire")
            else:
                rec.write({
                    'state': 'checked'
                })

    def confirm_action(self):
        for colis in self:
            if colis.invoice_ids:
                for invoice in colis.invoice_ids:
                    if invoice.payment_state == 'paid':
                        colis.write({
                            'ref': self.env['ir.sequence'].next_by_code("colis.expedition") or 'New',
                            'state': 'confirmed',
                        })
                    else:
                        raise ValidationError('La facture %s doit être totalement réglée avant de poursuivre' %
                                              invoice.name)
            else:
                raise ValidationError('La facturation de l\'élément est requise avant toute confirmation')

    def sent_action(self):
        for rec in self:
            if rec.price == 0:
                raise ValidationError('Le prix du service d\'expédition doit être supérieur à 0 FCFA')

            body = 'Salut %s, votre colis en partance pour %s vient d etre expedie. La reference du colis est: %s. ' \
                   'Nous vous remercions pour votre confiance' % (rec.sender_id.name, rec.from_place_id.name, rec.ref)
            response = sendSMS(rec.sender_id.phone, body)

            if response['responseCode'] == 200:
                rec.write({
                    'state': 'sent'
                })
            else:
                raise ValidationError('Error due à la notification du client')

    def set_canceled_action(self):
        for rec in self:
            rec.write({
                'state': 'canceled'
            })


class ColisProductLine(models.Model):
    _name = 'colis.product.line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Colis'

    product_id = fields.Many2one("product.product", string="Article", ondelete='cascade', tracking=True, required=True)
    quantity = fields.Integer("Quantité", default=1, tracking=True)
    weight = fields.Float("Poids (en Kg)", default=0, tracking=True, readonly=True, compute='_compute_weight')
    volume = fields.Float("Volume (en Kg)", default=0, tracking=True, readonly=True, compute='_compute_volume')
    colis_id = fields.Many2one("colis.expedition", ondelete='cascade', tracking=True)
    reception_id = fields.Many2one("colis.reception", ondelete='cascade', tracking=True, invisible=True)
    retrieve_id = fields.Many2one("colis.retrieve", ondelete='cascade', tracking=True, invisible=True)

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


class ColisTravel(models.Model):
    _name = 'colis.travel'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Travel'
    _rec_name = 'no'

    no = fields.Char('Numéro', required=True, tracking=True, index=True, copy=False)
    company_branch_id = fields.Many2one("res.company.branch", string="Agence", tracking=True)
