# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Rayito Reports",
    "summary": "Reports for Rayito",
    'version': '12.0.1.0.0',
    "category": "Invoicing & Payments",
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
        "partner_portal_extra_details",
    ],
    "data": [
        # reports
        "reports/invoice_report.xml",
        "reports/report_header.xml",
    ],
}
