{
    "name": "Sale & Purchase: Enviar por WhatsApp (WAHA Plus)",
    "version": "18.0.1.1.0",
    "summary": "Botão no Pedido de Venda e Compra para enviar PDF via WAHA Plus",
    "author": "Você",
    "license": "LGPL-3",
    "depends": [
        "base",
        "base_setup",
        "sale_management",
        "purchase",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
        "views/whatsapp_wizard_views.xml",
        "views/res_config_settings_view.xml",
        "data/params.xml",
    ],
    "installable": True,
    "application": False,
}