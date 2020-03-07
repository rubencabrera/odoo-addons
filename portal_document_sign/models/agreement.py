# Copyright 2020 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class DocumentBase(models.Model):
    """Base document for agreements"""
    _name = "documentbase"

    name = fields.Char(string="Nombre del documento", required=True)
    text = fields.Text(string="Texto del documento", required=True)
    date_start = fields.Date(string="Fecha de inicio")
    date_valid = fields.Date(string="Fecha de finalización")


class Agreement(models.Model):
    """Terms and conditions or other kinds of agreements to be
    signed by the user."""
    _name = "agreement"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre del documento", required=True)
    # TODO: Add relational to the tutor user in the system so these are
    #       computed.
    sign_name = fields.Char(string="Nombre completo de madre/padre/tutor")
    sign_legal = fields.Char(string="DNI/Pasaporte de madre/padre/tutor")
    signature = fields.Binary(string="Firma madre/padre/tutor")
    partner_id = fields.Many2one(comodel_name="res.partner", required=True)
    documentbase_id = fields.Many2one(
        comodel_name="documentbase", required=True)
