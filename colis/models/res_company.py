from odoo import api, fields, models, tools, _


class Company(models.Model):
  _inherit = "res.company"

  @api.model
  def _get_user_branch(self):
    try:
      user_branch = self.sudo().env.ref('base.main_company')
    except ValueError:
      user_branch = self.env['res.company'].sudo().search([], limit=1, order="id")
    return user_branch
