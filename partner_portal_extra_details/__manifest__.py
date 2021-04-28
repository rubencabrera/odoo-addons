# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Rayito Contact Details",
    "summary": "Extended contact details in user portal",
    'version': '12.0.1.0.0',
    "category": "Customer Relationship Management",
    "website": "https://github.com/rubencabrera/odoo-addons",
    "author": "Rubén Cabrera Martínez",
    "contributors": [
        'Rubén Cabrera Martínez <dev@rubencabrera.es>',
    ],
    "license": "AGPL-3",
    'application': False,
    'installable': True,
    'auto_install': False,
    "depends": [
        "partner_contact_personal_information_page",
        "partner_contact_birthdate",
        "partner_contact_gender",
        "account",
        "portal",
        "product",
        "l10n_es",
    ],
    "data": [
        #datas
        "data/product_template_data.xml",
        "data/mail_template_data.xml",
        #views
        "views/portal_templates.xml",
        "views/res_partner.xml",
        "views/res_company_views.xml",
        #wizard
        "wizard/automatic_partner_invoice.xml",
    ],
}
