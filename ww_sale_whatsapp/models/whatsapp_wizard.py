import base64
import logging
import requests
from requests.exceptions import RequestException
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class WhatsappWizard(models.TransientModel):
    _name = 'whatsapp.wizard'
    _description = 'Wizard para Envio de WhatsApp'

    phone = fields.Char(string="Telefone", required=True)
    message = fields.Text(string="Mensagem", required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', string="Anexos"
    )
    res_model = fields.Char('Modelo do Documento', readonly=True)
    res_id = fields.Integer('ID do Documento', readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        
        if active_model and active_id:
            record = self.env[active_model].browse(active_id)
            res.update({
                'res_model': active_model,
                'res_id': active_id,
                'phone': record.partner_id.mobile or record.partner_id.phone,
                'message': _("Olá, segue o documento %s em anexo.") % record.name,
            })
            
            attachment_id = False
            try:
                report_action = False
                if active_model == 'sale.order':
                    report_action = self.env.ref('sale.action_report_saleorder')
                elif active_model == 'purchase.order':
                    report_action = self.env.ref('purchase.action_report_purchase_order')

                if report_action:
                    # No Odoo 18, a função _render_qweb_pdf retorna 2 valores
                    pdf_content, _file_format = report_action._render_qweb_pdf(record.id)
                    
                    attachment = self.env['ir.attachment'].create({
                        'name': f"{record.name}.pdf",
                        'type': 'binary',
                        'datas': base64.b64encode(pdf_content),
                        'res_model': self._name,
                        'res_id': self.id,
                        'mimetype': 'application/pdf',
                    })
                    attachment_id = attachment.id
            except Exception as e:
                _logger.error(f"Falha ao gerar anexo PDF para {active_model} (ID: {record.id}): {e}")

            if attachment_id:
                res['attachment_ids'] = [(6, 0, [attachment_id])]
        return res

    def action_send_whatsapp(self):
        # Esta função permanece a mesma que já tínhamos
        self.ensure_one()
        config = self.env['ir.config_parameter'].sudo()
        base_url = config.get_param('whatsapp_integration.waha_base_url')
        api_key = config.get_param('whatsapp_integration.waha_api_key')
        session = config.get_param('whatsapp_integration.waha_session')

        if not base_url or not session:
            raise UserError(_("Configure a URL e a Sessão do WAHA nas Configurações do WhatsApp."))

        attachment = self.attachment_ids[0] if self.attachment_ids else None
        if not attachment:
            raise UserError(_("Nenhum anexo encontrado para envio."))
            
        url = f"{base_url.rstrip('/')}/api/sendFile"
        headers = {"X-Api-Key": api_key} if api_key else {}
        
        payload = {
            "chatId": f"{self.phone}@c.us",
            "caption": self.message,
            "session": session,
            "file": {
                "mimetype": attachment.mimetype,
                "filename": attachment.name,
                "data": attachment.datas.decode('utf-8'),
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            record = self.env[self.res_model].browse(self.res_id)
            record.message_post(body=_("Mensagem de WhatsApp enviada para %s.") % self.phone, attachment_ids=self.attachment_ids.ids)
        except RequestException as e:
            raise UserError(_("Erro ao enviar a mensagem: %s") % str(e))
        
        return {'type': 'ir.actions.act_window_close'}