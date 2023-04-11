# Copyright 2021 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2021 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    initial_template = fields.Many2one(
        comodel_name="mail.template",
        string="Plantilla de inicio de temporada",
    )

    payment_reminder_days = fields.Integer(
        string='Payment reminder days',
        help='Set the number of days to remind the user to make the payment. '
             'Set zero to don\'t send reminder.',
        default=3,
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Servicio a facturar",
        helps="El producto de tipo servicio que se usará para generar las facturas de cuota."
    )

    season_start = fields.Date(
        string="Fecha de inicio próxima temporada",
        help="""Fecha en la que se reiniciarán las casillas de participación en
        la presente temporada y se enviarán los emails de notificación a los
        jugadores. Esta fecha debe cambiarse cada año para que el proceso se
        repita.
        """
    )
