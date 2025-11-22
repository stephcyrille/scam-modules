
from odoo import api, fields, models


class ColisSaleOrder(models.Model):
    _inherit = 'colis.expedition'

    sale_order_ids = fields.One2many('sale.order', 'colis_sale_order_id', string='Bons de commande')
    sale_order_count = fields.Integer(compute='_compute_sale_data', string="Nombre de bon de commande")

    @api.depends('sale_order_ids.state')
    def _compute_sale_data(self):
        for colis in self:
            sale_order_count = 0
            for s_o in colis.sale_order_ids:
                if s_o.state in ('draft', 'sent'):
                    sale_order_count += 1
            colis.sale_order_count = sale_order_count

    def action_view_sale_order(self):
        return 0

    #def action create_


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    colis_sale_order_id = fields.Many2one("colis.expedition", ondelete='cascade', invisible=True)