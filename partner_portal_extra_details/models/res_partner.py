# Copyright 2020 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    """Adds simple emergency contact fields"""
    _inherit = "res.partner"

    tutor_phone = fields.Integer(string="Emergency phone")
    tutor_name = fields.Char(string="Nombre del contacto de emergencia")
