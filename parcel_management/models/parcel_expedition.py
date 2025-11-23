# -*- coding: utf-8 -*-
from odoo import models, fields, api, _



class ParcelExpedition(models.Model):
    _name = 'parcel.expedition'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = _('Parcel Expedition')
    _rec_name = 'ref'
    _order = 'date desc'

    ref = fields.Char(_('Référence'), required=True, tracking=True, index=True, copy=False, default="New", readonly=True)
    sender_id = fields.Many2one("res.partner", string=_("Sender"), tracking=True, required=True)
    receiver_id = fields.Many2one("res.partner", string=_("Recipient"), tracking=True, required=True)
    driver_id = fields.Many2one("res.partner", string=_("Driver"), tracking=True)
    plate_no = fields.Char(_('License Plate'), tracking=True, index=True)
    parcel_type_id = fields.Many2one("parcel.type", string=_("Parcel Type"), tracking=True, required=True)
    # travel_no = fields.Many2one("colis.travel", string="N° du voyage", tracking=True)
    from_warehouse_id = fields.Many2one("stock.warehouse", string=_("From Warehouse"), tracking=True, required=True,
                                        help=_('Location where the parcel is stored before being shipped to the agency'),
                                        default=lambda self: self._get_the_warehouse_from_origin_branch())
    to_warehouse_id = fields.Many2one("stock.warehouse", string=_("To Warehouse"), tracking=True,
                                      help=_('Location where the parcel is stored upon arrival at the agency'))
    # current_warehouse_id = fields.Many2one("stock.warehouse", string=_("Current Warehouse"), tracking=True)
    # current_location_id = fields.Many2one("stock.location", string=_("Current Location"), tracking=True,
    #                                       help=_('This is the exact location where the item is situated in the warehouse. '
    #                                              'When the item is in the sent status, this value will be null.'),
    #                                              domain="[('usage', 'in', ['internal', 'transit', 'customer'])]")
    operator_id = fields.Many2one("res.users", string=_("Operator"), tracking=True, required=True,
                                  help=_('Operator responsible for entering the parcel information, by default the connected user is selected'),
                                  default=lambda self: self.env.user)
    from_place_id = fields.Many2one("parcel.city", string=_("Departure City"), tracking=True, required=True,
                                    help=_('City of departure'))
    to_place_id = fields.Many2one("parcel.city", string=_("Arrival City"), tracking=True, required=True,
                                  help=_('City of arrival'))
    weight = fields.Float(_("Weight (in Kg)"), default=0, tracking=True, readonly=True, compute='_compute_total_weight')
    capacity = fields.Float(_("Volume (in m3)"), default=0, tracking=True, readonly=True,
                            compute='_compute_total_capacity')
    price = fields.Float(_("Service Price"), default=0, tracking=True, readonly=True)
    currency_id = fields.Many2one(
        'res.currency', _('Currency'), compute='_compute_currency_id')
    description = fields.Text()
    date = fields.Date(_("Registration Date"), tracking=True, default=fields.Date.today(), readonly=True)
    departure_date = fields.Date(_("Departure Date"), tracking=True, required=True)
    estimated_arrival_date = fields.Date(_("Estimated Arrival Date"), tracking=True, required=True)
    state = fields.Selection([
        ('draft', _('Draft')),
        ('checked', _('Checked')),
        ('confirmed', _('Confirmed')),
        ('sent', _('Sent')),
        ('canceled', _('Canceled')),
        ('arrived', _('Arrived')),
        ('end', _('Picked Up'))], 
        string=_('Status'), copy=False, default='draft', index=True, readonly=True, tracking=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env['res.company']._get_main_company())
    origin_branch_id = fields.Many2one(
        "res.company",
        string=_("Origin Branch"),
        tracking=True,
        help=_('Branch where the parcel is located'),
        default=lambda self: self._get_the_first_branch(),
    )
    destination_branch_id = fields.Many2one(
        "res.company",
        string=_("Destination Branch"),
        tracking=True,
        help=_('Branch where the parcel is going'),
    )
    parcel_product_ids = fields.One2many('parcel.product.line', 'parcel_id', string=_('Articles'), tracking=True)
    parcel_services_ids = fields.One2many('parcel.service.line', 'parcel_id', string=_('Services fees'), tracking=True)


    def default_get(self, fields):
        res = super(ParcelExpedition, self).default_get(fields)
        product = self.env.ref('parcel_management.product_parcel_expedition_fees')  # XML ID of your product
        if product and 'parcel_services_ids' in fields:
            res['parcel_services_ids'] = [(0, 0, {
                'product_id': product.product_variant_id.id,  # Use variant ID for sale.order.line
                'product_uom_qty': 1,
                'price_unit': product.list_price,
            })]
        return res


    def _get_the_first_branch(self):
        """ Returns the first branch of the company """
        try:
            return self.env.companies[0]
        except Exception as e:
            return self.env.company

    def _get_the_warehouse_from_origin_branch(self):
        """ Returns the default warehouse of the company branch """
        try:
            warehouse = self.env['stock.warehouse'].search([(
                'company_id', '=', self.env.companies[0].id)], limit=1)
            return warehouse.id if warehouse else False
        except Exception as e:
            warehouse = self.env['stock.warehouse'].search([(
                'company_id', '=', self.env.company.id)], limit=1)
            return warehouse.id if warehouse else False

    @api.depends('company_id')
    def _compute_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id

    @api.depends('parcel_product_ids.weight')
    def _compute_total_weight(self):
        self.ensure_one()
        weight = 0
        for line in self.parcel_product_ids:
            weight += line.weight or 0.0
        self.weight = weight

    @api.depends('parcel_product_ids.volume')
    def _compute_total_capacity(self):
        self.ensure_one()
        volume = 0
        for line in self.parcel_product_ids:
            volume += line.volume or 0.0
        self.capacity = volume

    @api.onchange('sender_id')
    def _onchange_sender_id(self):
        """ Update the sender's city, state, and country when sender_id is changed """
        if self.sender_id:
            self.from_place_id = self.sender_id.parcel_city_id
        else:
            self.from_place_id = False

    @api.onchange('receiver_id')
    def _onchange_receiver_id(self):
        """ Update the receiver's city, state, and country when receiver_id is changed """
        if self.receiver_id:
            self.to_place_id = self.receiver_id.parcel_city_id
        else:
            self.to_place_id = False
