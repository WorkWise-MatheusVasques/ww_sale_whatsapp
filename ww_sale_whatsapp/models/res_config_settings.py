import requests
from requests.exceptions import RequestException
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    waha_base_url = fields.Char(
        string="URL Base do WAHA",
        config_parameter="whatsapp_integration.waha_base_url",
        help="Ex.: http://localhost:3000"
    )
    waha_api_key = fields.Char(
        string="Chave da API (API Key)",
        config_parameter="whatsapp_integration.waha_api_key"
    )
    waha_session = fields.Char(
        string="Nome da Sessão",
        config_parameter="whatsapp_integration.waha_session",
        default="default"
    )

    def action_test_waha_connection(self):
        self.ensure_one()
        if not self.waha_base_url:
            raise UserError(_("Por favor, informe a URL Base do WAHA."))

        url = f"{self.waha_base_url.rstrip('/')}/api/sessions"
        headers = {"X-Api-Key": self.waha_api_key} if self.waha_api_key else {}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            sessions = response.json()
            session_names = [s.get('name', '') for s in sessions]
            message = _("Conexão bem-sucedida! Sessões encontradas: %s") % ", ".join(session_names)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Sucesso"),
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                }
            }
        except RequestException as e:
            raise UserError(_("Falha na conexão com o WAHA: %s") % str(e))