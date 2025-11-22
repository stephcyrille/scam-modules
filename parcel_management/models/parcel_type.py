# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

    
class ParcelType(models.Model):
    _name = 'parcel.type'
    _description = _('Parcel Type')
    _rec_name = 'name'

    code = fields.Char(_('Code'), required=True)
    name = fields.Char(_('Name'), required=True)
    description = fields.Text(_('Description'), help=_('A brief description of the parcel type.'))
    active = fields.Boolean(_('Active'), default=True, help=_('Indicates whether this parcel type is currently active.'))