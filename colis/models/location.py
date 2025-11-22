from odoo import models, fields, api


class StockLocation(models.Model):
    _description = 'Types de colis'
    _inherit = ['stock.location']

    company_branch_id = fields.Many2one("res.company.branch", string="Agence")
