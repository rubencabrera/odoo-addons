# Copyright 2021 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2021 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Service to invoice"
    )
    payment_reminder_days = fields.Integer(
        string='Payment reminder days',
        help='Set the number of days to remind the user to make the payment. '
             'Set zero to don\'t send reminder.',
        default=3,
    )