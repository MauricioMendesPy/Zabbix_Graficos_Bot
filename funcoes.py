from datetime import datetime, timezone
import requests
import urllib3
from zabbix_api import ZabbixAPI
from configuracoes import *


#CLASSE PARA LIDAR COM VARIOS ACESSOS AO ZABBIX
class ZabbixUser:
    def __init__(self):
        self.login = None
        self.senha = None
        self.zapi = None

    def login_zabbix(self, login, senha):
        self.login = login
        self.senha = senha
        self.dict_tratado = {}
        self.trigger_id_dict = {}
        self.event_id_dict = {}
        self.host_id_dict = {}
        self.dict_agrupado = {}
        self.dict_clock_evento = {}
        self.grupos_dict = {}
        self.host_graph_agrupados = {}
        self.item_name_graph = {}
        self.graph_item = {}
        self.reco_message = ""
        self.id_grafico = ""
        
        try:
            self.zapi = ZabbixAPI(url_zab)
            self.zapi.login(login, senha)
            return True
        except Exception as e:
            print(e)
            return False


users = {}

#FUNÇÃO PARA LIDAR COM TIME-STAMPS
def formatar_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp)


#LOGAR NO FRONT DO ZABBIX PARA MONTAR O GRÁFICO
def gerar_grafico(id_grafico,periodo):
    urllib3.disable_warnings()
    
    if lang_front == "US":
        action_text = "Sign in"

    else:
        action_text = "Conectar-se"

    login_data = {
    "name": user_admin,
    "password": senha_admin,
    "enter": action_text
                        }
    
    obter_cookies = requests.post(url_zab + "/", data=login_data, verify=True)
    cookies = obter_cookies.cookies


    link_dos_graficos = f"{url_zab}/chart2.php?graphid={id_grafico}&from=now-{str(periodo)}h&to=now&height=250&width=1000&profileIdx=web.charts.filter"
    grafico_zabbix = f"Grafico_{periodo}.png"

    grafico_request = requests.get(link_dos_graficos,cookies=cookies)
    grafico_resource = grafico_request.content

    with open(grafico_zabbix,'wb') as zab_grafico:
        zab_grafico.write(grafico_resource)
    
    return grafico_zabbix


#CLASSE PARA CRIAR UM MENU DE BOTÕES
class Paginacao:
    def __init__(self, items):
        self.items = items

    def criar_pagina(self, pagina, items_por_pagina,prefixo):
        '''
        CRIA UMA PAGINAÇÃO PARA OS BOTÕES

        PARAMETROS:
        pagina ->  número de página desejada
        items_por_pagina -> define quantos itens você quer por página
        prefixo -> prefixo para ser tratado na paginação

        RETURN:
        MENU PAGINADO

        '''
        Menu = types.InlineKeyboardMarkup()
        
        # CALCULA OS ITENS POR PAGINA
        primeiro_indice = (pagina - 1) * items_por_pagina
        ultimo_indice = primeiro_indice + items_por_pagina
        items_plotados = self.items[primeiro_indice:ultimo_indice]

        # ADICIONA OS ITEMS POR PAGINA,DEFINIDOS EM ARGS
        for item in items_plotados:
            Menu.add(types.InlineKeyboardButton(text=item[:50], callback_data=item[:50]))

        # BOTÕES DE NAVEGAÇÃO
        navigation_buttons = []
        if pagina > 1:
            navigation_buttons.append(types.InlineKeyboardButton(text='⬅️ Anterior', callback_data=f'page_{pagina-1},{prefixo}'))
        if ultimo_indice < len(self.items):
            navigation_buttons.append(types.InlineKeyboardButton(text='➡️ Próxima', callback_data=f'page_{pagina+1},{prefixo}'))

        Menu.row(*navigation_buttons)

        return Menu