# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ParcelProductTemplate(models.Model):
    _inherit = 'product.template'

    is_a_parcel = fields.Boolean(string=_("Is a parcel"), default=False)
    # I just wwant to use it for hidding the type field in the form of product
    hide_type_field = fields.Boolean(string=_("Hide the type"), default=False)
