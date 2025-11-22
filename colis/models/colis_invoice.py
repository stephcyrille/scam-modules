
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ColisInvoice(models.Model):
    _inherit = 'colis.expedition'

    invoice_count = fields.Integer(compute='_compute_invoice_data', string="Nombre de factures", store=True)
    invoice_ids = fields.One2many('account.move', 'colis_invoice_id', string='Orders')

    @api.depends('invoice_ids.state')
    def _compute_invoice_data(self):
        for colis in self:
            invoice_cnt = 0
            for invoice in colis.invoice_ids:
                if invoice.state in ('draft', 'posted'):
                    invoice_cnt += 1
            colis.invoice_count = invoice_cnt
            print("\n\nCount: %s\n\n" % colis.invoice_count)

    def action_view_invoice(self):
        for rec in self:
            if len(rec.invoice_ids) > 0:
                action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
                action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
                action['res_id'] = rec.invoice_ids[0].id
                return action

    def action_create_invoice(self):
        for rec in self:
            action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
            action['context'] = {
                'search_default_draft': 1,
                'search_default_partner_id': rec.sender_id.id,
                'default_partner_id': rec.sender_id.id,
                'default_move_type': 'out_invoice',
                'default_invoice_date': rec.date,
                'default_colis_invoice_id': rec.id
            }
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = False
            return action


class AccountMove(models.Model):
    _inherit = 'account.move'

    colis_invoice_id = fields.Many2one("colis.expedition", ondelete='cascade', invisible=True)

    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
    #     for rec in self:
    #         try:
    #             colis_id = self.env['colis.colis'].search([('id', '=', rec.colis_invoice_id.id)])
    #             colis_id.write({'state': 'confirmed'})
    #         except Exception as e:
    #             raise ValidationError("Error on invoice confirmation: %s" % e.__str__())
    #     return res