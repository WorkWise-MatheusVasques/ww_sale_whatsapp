import base64
import requests
from requests.exceptions import RequestException
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class WhatsappWizard(models.TransientModel):
    _name = 'whatsapp.wizard'
    _description = 'Wizard para Envio de WhatsApp'

    phone = fields.Char(string="Telefone", required=True)
    message = fields.Text(string="Mensagem", required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', string="Anexos"
    )
    
    # Campos para guardar a referência do documento de origem
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
            
            # Gera e anexa o PDF padrão
            report_action = self.env['ir.actions.report']._get_report_from_name(
                'sale.report_saleorder' if active_model == 'sale.order' else 'purchase.report_purchaseorder'
            )
            pdf_content, _ = report_action._render_qweb_pdf(record.id)
            
            attachment = self.env['ir.attachment'].create({
                'name': f"{record.name}.pdf",
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': self._name, # Anexo temporário para o wizard
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })
            res['attachment_ids'] = [(6, 0, [attachment.id])]
        return res

    def action_send_whatsapp(self):
        self.ensure_one()
        
        # Carrega configurações
        config = self.env['ir.config_parameter'].sudo()
        base_url = config.get_param('whatsapp_integration.waha_base_url')
        api_key = config.get_param('whatsapp_integration.waha_api_key')
        session = config.get_param('whatsapp_integration.waha_session')

        if not base_url or not session:
            raise UserError(_("Configure a URL e a Sessão do WAHA nas Configurações do Odoo."))

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
            
            # Adiciona nota no chatter
            record = self.env[self.res_model].browse(self.res_id)
            record.message_post(
                body=_("Mensagem de WhatsApp enviada para %s.") % self.phone,
                attachment_ids=self.attachment_ids.ids
            )
            
        except RequestException as e:
            raise UserError(_("Erro ao enviar a mensagem: %s") % str(e))
        
        return {'type': 'ir.actions.act_window_close'}