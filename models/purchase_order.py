from odoo import models, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_open_whatsapp_wizard(self):
        self.ensure_one()
        return {
            'name': _('Enviar por WhatsApp'),
            'type': 'ir.actions.act_window',
            'res_model': 'whatsapp.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'purchase.order',
                'active_id': self.id,
            }
        }