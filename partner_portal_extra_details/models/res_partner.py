# Copyright 2020 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    """Adds simple emergency contact fields"""
    _inherit = "res.partner"

    tutor_phone = fields.Char(string="Emergency phone")
    tutor_name = fields.Char(string="Nombre del contacto de emergencia")
    validate_portal_user = fields.Boolean(
        string="Validate portal user",
        help="Allows to validate the user registered in the portal."
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Service to invoice"
    )

    @api.multi
    def write(self, values):
        if values.get('validate_portal_user'):
            self._send_mail_to_new_validate_user()
        return super(ResPartner, self).write(values)

    @api.multi
    def _send_mail_to_new_validate_user(self):
        """
        This function sends an email to the new validated user of the portal.
        """
        self.ensure_one()
        AccountInvoice = invoices = self.env['account.invoice']
        dom = [
            ('partner_id', '=', self.id),
            ('state', '=', 'draft')
        ]
        invoices |= AccountInvoice.search(
            dom, order='date_invoice asc', limit=1
        )
        if not invoices:
            invoices |= self._create_partner_invoice()
        invoices._send_payment_terms_mail()

    def _create_partner_invoice(self):
        self.ensure_one()
        partner = self
        AccountInvoice = self.env['account.invoice']
        invoice_line_values = self._prepare_invoice_line_values()
        company_id = partner.company_id
        origin = self._get_invoice_origin()
        values = {
            'type': 'out_invoice',
            'reference': partner.name,
            'partner_id': partner.id,
            'date_invoice': fields.Date.today(),
            'invoice_line_ids': invoice_line_values,
            'currency_id': company_id.currency_id.id,
            'company_id': company_id.id,
            'origin': origin
        }
        invoice = AccountInvoice.new(values)
        invoice._onchange_partner_id()
        invoice = AccountInvoice.create(values)
        return invoice

    def _get_invoice_origin(self):
        self.ensure_one()
        return '{} {} {}'.format(
            self.firstname, self.lastname, self.lastname2
        )

    def _prepare_invoice_line_values(self):
        self.ensure_one()
        product = self.product_id
        if not product:
            raise UserError(
                _('You must select the service to create invoice.')
            )
        account_id = product.categ_id.property_account_income_categ_id
        values = [(0, 0, {
            'name': product.name,
            'origin': 'Factura de registro',
            'account_id': account_id.id,
            'price_unit': product.list_price,
            'quantity': 1.0,
            'uom_id': product.uom_id.id,
            'product_id': product.id,
            'invoice_line_tax_ids': [(6, 0, [product.taxes_id.id])],
        })]
        return values
