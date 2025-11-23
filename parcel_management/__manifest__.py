# -*- coding: utf-8 -*-
{
    'name': "Parcel Management",

    'summary': "Manage parcels, shipments, and delivery tracking within Odoo.",

    'description': """
        This module provides a comprehensive solution for managing parcels, including shipment creation, tracking, and delivery confirmation.
        It integrates with Odoo's existing sales and inventory modules to streamline the parcel management process.
        Key features include:
        - Create and manage shipments
        - Track parcel status and delivery
        - Integration with sales orders and inventory
        - User-friendly interface for managing parcel details
        - Notifications for shipment updates
        - Reporting tools for shipment performance analysis
        - Customizable settings for different parcel types and delivery methods
        - Support for multiple carriers and shipping options
        - Easy integration with Odoo's portal for customer access to shipment information
    """,

    'author': "SCMA Consulting",
    'website': "https://www.scma-consulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Shipping',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'portal', 'utm', 'stock', 'sale_management'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/config/parcel_city_views.xml',
        'views/parcel/parcel_expedition_views.xml',
        'views/parcel/parcel_type_views.xml',
        'views/menu.xml',

        # Base views
        'views/base/partner_views.xml',
        'views/base/product_template_inherited_views.xml',

        # Loading records
        'data/parcel/cities.xml',
        'data/parcel/parcel_types.xml',
        'data/parcel/product.xml',
        #  Loading sequences
        # 'data/sequences/sequences.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'application': True,
}

