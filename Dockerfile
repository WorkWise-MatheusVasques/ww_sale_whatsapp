# Use a imagem oficial do Odoo 18 como base
FROM odoo:18.0

# Mude para o usuário root para instalar pacotes
USER root

# Instala a biblioteca 'requests' que é uma dependência do módulo customizado
RUN pip3 install requests

# Copia o módulo customizado para o diretório de addons do Odoo no contêiner
COPY ./ww_sale_whatsapp /mnt/extra-addons/ww_sale_whatsapp

# Define o usuário 'odoo' como proprietário da pasta de addons
RUN chown -R odoo:odoo /mnt/extra-addons

# Retorna para o usuário padrão do Odoo
USER odoo