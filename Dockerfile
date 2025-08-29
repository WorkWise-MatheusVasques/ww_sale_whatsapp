# 1. Usar a imagem oficial do Odoo 18 como base
FROM odoo:18.0

# 2. Mudar para o usuário root para instalar pacotes
USER root

# 3. --- CORREÇÃO DE AMBIENTE ---
# Instala todos os pacotes de localização. Isso previne erros de
# inicialização de banco de dados em alguns ambientes.
RUN apt-get update && apt-get install -y locales-all

# 4. Instala a biblioteca 'requests' do Python
RUN pip install requests --break-system-packages

# 5. Retorna para o usuário padrão do Odoo para segurança
USER odoo