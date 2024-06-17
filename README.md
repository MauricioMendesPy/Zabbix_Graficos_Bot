## Doações

| <img width="50" height="50" src="https://user-images.githubusercontent.com/741969/99538099-3b7a5d00-298b-11eb-9f4f-c3d0cd4a5280.png" /> | <code>mauriciomendesoares@gmail.com</code> |
| --- | --- |



# Zabbix Menu Bot

bot de automaçao no <b>Zabbix</b> para reconhecimento e busca de gráficos.

#### Como foi pensado

O bot foi construido para ser simples e eficiente com o principal objetivo de permitir que usuários sem acesso ao front do Zabbix possam reconhecer incidentes
e obter imagem dos gráficos.

### Como usar:

- Crie um bot no telegram com o BotFather e obtenha a <b>HTTP API</b>
<img widht=150 height=150 src="https://github.com/MauricioMendesPy/Zabbix_Graficos_Bot/assets/148800324/4e8b75e5-5827-4660-9f5f-db1587c1bd86" />

- Faça o clone do repositório em qualquer pasta do seu servidor
  <pre><code>git clone https://github.com/MauricioMendesPy/Zabbix_Graficos_Bot.git </code></pre>

- Crie um ambiente virtual e faça a instalação do requirements após ter <strong>ativado</strong> seu ambiente.
  <pre>python3 -m venv "Seu Ambiente"</pre>
  <pre>pip install -r requirements.txt</pre>
  coloque os arquivos dentro do seu env:
  <blockquote>Configuracoes.py</blockquote>
  <blockquote>Funcoes.py</blockquote>
  <blockquote>menu_zabbix.py</blockquote>
    
    

- Configure os campos no arquivo Configuracoes.py

lembre-se que a URL do Zabbix precisa conter "http://IP_DO_ZABBIX/zabbix"

  ```python
    #CONFIGURAÇÕES DO     TELEGRAM----------------------------------------------#
    api_token = "TOKEN DO SEU BOT"
    bot = TeleBot(api_token)
    #ZABBIX------------------------------------------------------------------#
    url_zab = "URL DO SEU ZABBIX"
    user_admin = "LOGIN ADMIN"
    senha_admin = "SENHA ADMIN"



  
- Valide se deu tudo certo usando como interpretador o python do seu env:
  <pre>/home/pasta_do_seu_env/bin/ptyhon3 /home/pasta_do_seu_env/menu_zabbix.py</pre>
  mostrará algo assim:

- volte no bot que você criou e digite o comando
<pre>/inicio</pre>
retornará:
<img widht=150 height=150 src="https://github.com/MauricioMendesPy/Zabbix_Graficos_Bot/assets/148800324/d318a917-5224-43e9-8619-b0da47f6333a" />
<br><br>
## Funcionamento do BOT

- Login no Zabbix pelo Bot fazendo com que cada tratativa leve o nome do usuário Logado.
- Paginação de InlineButtons - Caso você posua em seu Zabbix muitos HostGroups, Hosts e Itens o bot faz uma paginação dos botões criados
- Busca de Gráficos trazendo itens que já possuem gráficos criados no Zabbix.
- <img widht=150 height=150 src="https://github.com/MauricioMendesPy/Zabbix_Graficos_Bot/assets/148800324/375e927f-95db-472e-8e46-89b8b349759e" />



  
## Criando um arquivo <b>.service</b> para deixar o bot como serviço

- entre na pasta:
<pre>cd /etc/systemd/system/</pre>
- crie um arquivo com nome "NOME_DO_SERVICO".service
  <pre>nano zabbix_bot.service</pre>
  
  <pre>[Unit]
  Description=Zabbix_Reconhecimento
  After=network.target

  [Service]
  User=root
  ExecStart=/home/seu_env/bin/python3 -u /home/seu_env/menu_zabbix.py
  Restart=always
  RestartSec=10
  
  [Install]
  WantedBy=multi-user.target</pre>

salve o arquivo e execute os comandos:
<pre> systemctl daemon-reload</pre>
<pre>systemctl start "SEU_SERVIÇO".service</pre>
mostrará assim:
<img widht=150 height=150 src="https://github.com/MauricioMendesPy/Zabbix_Graficos_Bot/assets/148800324/3777016b-8fac-4f8b-99a8-1e65ba8546b4" />



Assim o bot ficará rodando como serviço e você pode consultar os logs com o comando:
<pre>journalctl -u "SEU_SERVIÇO".service</pre>
ver ultimas 100 linhas
<pre>journalctl -u "SEU_SERVIÇO".service -n 100 </pre>
 

