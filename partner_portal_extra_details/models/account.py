# Copyright 2021 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2021 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _send_payment_terms_mail(self):
        template = self._get_payment_term_template()
        for record in self:
            record._send_mail_to_new_partner(template)

    def _send_mail_to_new_partner(self, template):
        self.ensure_one()
        template.send_mail(self.id, force_send=True)

    def _get_payment_term_template(self):

        module_name = 'partner_portal_extra_details'
        template = self.env.ref(
            "%s.email_template_send_user_payment_term" % module_name
        )
        return template
