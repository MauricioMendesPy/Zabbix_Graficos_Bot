# -*- coding: utf-8 -*-
###########################################################################################
#                                Desenvolvido por                                         #
#                             Mauricio Mendes Soares                                      #
#-----------------------------------------------------------------------------------------#                                                                                         
#                                                                                         #
#                             Linkedin - MauricioMendesPy                                 #
#-----------------------------------------------------------------------------------------#                                                                                         #
#                                                                                         #
#                          TESTADO NA VERSÃO 6.0.25 -ZABBIX                               #                              
#                         NÃO RETIRE OS CRÉDITOS POR GENTILEZA                            #
#                                                                                         #
#                                                                                         #
#                                                                                         #
###########################################################################################
from configuracoes import *
from funcoes import ZabbixUser,Paginacao,formatar_timestamp,gerar_grafico



users = {}

@bot.message_handler(commands=['inicio'])
def MenuInicio(message):
    
    chat_id = message.chat.id
    usu = message.from_user.first_name


    if chat_id not in users:
        users[chat_id] = ZabbixUser()
    

    bot.send_message(
        message.chat.id,(

f'''Olá <b>{usu}</b>{e_ola}
Para utilizar as configurações do BOT você precisa estar logado no 
<b>Zabbix</b>

Digite seu login por gentileza:
'''),
        parse_mode="HTML"
        )
    
    bot.register_next_step_handler(message,getlogin)

@bot.message_handler(func=lambda message: message.chat.id in users and users[message.chat.id].login is None)
def getlogin(message):
    
    chat_id = message.chat.id
    
    users[chat_id].login = message.text

    bot.send_message(message.chat.id,"Digite sua senha")
    bot.register_next_step_handler(message,get_senha)


@bot.message_handler(func=lambda message: message.chat.id in users and users[message.chat.id].login is not None and users[message.chat.id].senha is None)
def get_senha(message):
    chat_id = message.chat.id
    users[chat_id].senha = message.text

    if users[chat_id].login_zabbix(users[chat_id].login, users[chat_id].senha):
        menu_principal(message)
    else:
        bot.send_message(
            message.chat.id,
            "Não foi possivel logar em sua conta, tente novamente"
            )
        
        MenuInicio(message)
# LOGIN ZABBIX FIM ------------------------------------------------------------------------------------------------#






#####################################################################################################################
############################-----------------INICIO DO BOT-----------################################################
#####################################################################################################################

def menu_principal(message):

    menu = types.InlineKeyboardMarkup(row_width=2)


    Reconhecimento = types.InlineKeyboardButton(f"{e_certo} Reconhecimento",callback_data="Reco") # < callback para chamada no acionamento no botão
    obter_graficos = types.InlineKeyboardButton(f"{e_graph} Gráficos",callback_data="Graph") # < callback para chamada no acionamento no botão


    menu.add(Reconhecimento,obter_graficos)


    bot.send_message(
        message.chat.id,
        "Bem vindo ao Bot de Reconhecimento e Busca de Gráficos no Zabbix\n Escolha uma das opções" ,
        reply_markup=menu,parse_mode="HTML"
        )




#FUNÇÃO ISOLADA PARA RECONMHECIMENTO DOS INCIDENTES ---------------------------------------- #
def reconhecimento(message,**dict):
    if message.text == "sair":
        menu_principal(message)
    else:
        chat_id = message.chat.id
        users[chat_id].reco_message = ""

        dict_message = dict.get('dict_message')
        users[chat_id].reco_message = message.text
        for event_id in dict_message.values():

        
            #ADICIONA 3 TIPO DE TRATATIVA AO EVENTO - 2- ACKNOWLEDGE - 4 - ADD MESSAGE - 8 - CHANGE SEVERITY
            users[chat_id].zapi.event.acknowledge({"eventids":event_id,"action":2|8|4,'message':users[chat_id].reco_message,'severity':1})
        bot.send_message(message.chat.id, "Trigger Reconhecida com Sucesso, Obrigado")

        return menu_principal(message)
        
    



@bot.callback_query_handler(func=lambda call:call.data == "Reco")
def callbacks(call):
    chat_id = call.message.chat.id


    if chat_id not in users:
        bot.send_message(
        chat_id,
        "Você precisa estar logado no zabbix para utilizar as funções"
    )

        MenuInicio(call.message)
    else:


        obter_triggers = users[chat_id].zapi.trigger.get({
            'output': ['triggerids', 'description'], 
            'selectHosts': ["name","hostid"],
            'monitored': True,
            'selectLastEvent':['eventid','clock'],
            'filter':{"value":1},
            'only_true':True,
            'selectItems':['name','itemid'],
            'expandDescription': True,
            'sortfield': 'lastchange',
            'sortorder': 'DESC',
            'withLastEventUnacknowledged':True
        
        })

        print(f'OBTER_TRIGGERS_RAIZ {obter_triggers}\n\n\n')


        #TRIGGERID COM DESCRIÇÃO DO EVENTO -------------------------------------#
        users[chat_id].trigger_id_dict = {trig['triggerid']:trig['description'] for trig in obter_triggers}
        #TRIGGERID COM COM ID DO EVENTO -------------------------------------#
        users[chat_id].event_id_dict = {event_id['triggerid']:event_id['lastEvent']['eventid'] for event_id in obter_triggers}
        #TRIGEGRID COM HOST
        users[chat_id].host_id_dict = {host_id['triggerid']:host_id['hosts'][0]['name'] for host_id in obter_triggers}
        #TRIGGER ID COM CLOCK
        users[chat_id].dict_clock_evento = {event_clock['triggerid']:event_clock['lastEvent']['clock'] for event_clock in obter_triggers}

        
            
        #AGRUPA OS HOSTS COM INCIDENTES ALARMADOS
        for tg,host in users[chat_id].host_id_dict.items():
            if host not in users[chat_id].dict_agrupado:
                users[chat_id].dict_agrupado[host] = []
            if tg not in users[chat_id].dict_agrupado[host]:
                users[chat_id].dict_agrupado[host].append(tg)



        #GERAÇÃO DO PRIMEIRO MENU COM OS HOSTS QUE CONTÉM TRIGGERS
        menu_incientes = types.InlineKeyboardMarkup(row_width=3)
        for host_name , triggers_ids in users[chat_id].dict_agrupado.items():

            botoes_hosts = types.InlineKeyboardButton(f'{host_name} - Triggers: {len(triggers_ids)}',callback_data=host_name)
            menu_incientes.add(botoes_hosts)
        
        if obter_triggers == []:
            bot.send_message(
            call.message.chat.id,
            "Não possui nenhum  Host com trigger sem reconhecimento, Obrigado.",
            reply_markup=menu_incientes

        )
            menu_principal(call.message)
        else:

            bot.send_message(
                call.message.chat.id,
                "Selecione um Host para reconhecer um incidente",
                reply_markup=menu_incientes

            )
#FUNÇÃO PARA LIDAR COM OS BOTÕES AGRUPADOS POR HOST
@bot.callback_query_handler(func=lambda call:call.data if call.data in users[call.message.chat.id].host_id_dict.values() else False)
def callbacks(call):
    chat_id = call.message.chat.id



    menu_triggers = types.InlineKeyboardMarkup(row_width=2)
    for h_name,t_ids in users[chat_id].dict_agrupado.items():
        if call.data == h_name:
            for ids in t_ids:
                for t_id,t_desc in users[chat_id].trigger_id_dict.items():
                    if ids == t_id:
                        button_id = types.InlineKeyboardButton(t_desc,callback_data=t_desc)
                        menu_triggers.add(button_id)
    
            
    bot.send_message(
        call.message.chat.id,
        f"Selecione uma trigger do Host: \n*{call.data}*\n",
        reply_markup=menu_triggers,parse_mode="Markdown"

    )

#COMO SÃO CRIADOS N BOTÕES É DEFINIDO UMA LAMBDA COMO ARGUMENTO DO DECORATOR PARA LIDAR COM ACIONAMENTO DA CADA BOTÃO                    
@bot.callback_query_handler(func=lambda call:call.data if call.data in users[call.message.chat.id].trigger_id_dict.values() else False)
def callbacks(call):
    print(f"TRIGGER SELECIONADA : {call.data}")
    chat_id = call.message.chat.id

    #QUANDO UM BOTÃO DE UMA TRIGGER FOR SELECIONADO, VERIFICA NO DICT DE EVENTO O ID DO EVENTO PARA RECONHECIMENTO
    for t_id , t_descr in users[chat_id].trigger_id_dict.items():
        for t_id_event , id_event in users[chat_id].event_id_dict.items():
            if call.data == t_descr:
                if t_id == t_id_event:
                    users[chat_id].dict_tratado[t_id] = id_event #ARMAZENA A TRIGGER ID E O ID DO EVENTO


    dict_clock = {}
    for trigger_id_clock , clock in users[chat_id].dict_clock_evento.items():
        for t , event_id in users[chat_id].dict_tratado.items():
            if trigger_id_clock == t:
                dict_clock[call.data] = clock


    #FAZ A VERIFICAÇÃO DO EVENTO COM O HORARIO
    print(f'DICT_TRATADO: \n{users[chat_id].dict_tratado}\n\n\n')

            
    
    bot.send_message(
        chat_id,
        f"Digite a mensagem de Reconhecimento para:\n *{call.data}*\n  Ultimo alarme: \n*{formatar_timestamp(int(dict_clock[call.data]))}*\n\n Caso desista do Reconhecimento basta digitar *sair*\n\n",
        parse_mode="Markdown",

    )
    bot.register_next_step_handler(
        call.message,
        reconhecimento,dict_message=users[chat_id].dict_tratado #-> RECONHECIMENTO, FUNÇÃO APARTADA

    )
        
       
    
    
#####################################################################################################################
############################-----------------Gráficos-----------#####################################################
#####################################################################################################################


@bot.callback_query_handler(func=lambda call:call.data == "Graph")
def callbacks_hostgroup(call):

    pagina = 1
    items_por_pagina = 8
    prefixo = "hgroup"


    chat_id = call.message.chat.id


    if chat_id not in users:
        bot.send_message(
        chat_id,
        "Você precisa estar logado no zabbix para utilizar as funções"
    )

        MenuInicio(call.message)
    else:
        

        groups_get = users[chat_id].zapi.hostgroup.get({
            "output":['groupid','name'],
            "with_graphs":True,
            'real_hosts':True 

        })

       
        
            
        #ARMAZENA TODOS OS HOST_GROUPS_IDS QUE POSSUEM GRAFICOS
        users[chat_id].grupos_dict = {h_groups['groupid']: h_groups['name'] for h_groups in groups_get}
        
        if users[chat_id].grupos_dict == {}:
            bot.send_message(chat_id, "Não foi possivel localizar nenhum gáfico com base no seu Login")
            menu_principal(call.message)
        else:
            paginas = Paginacao(list(users[chat_id].grupos_dict.values()))
    
            menu = paginas.criar_pagina(pagina, items_por_pagina,prefixo)
           
            bot.send_message(chat_id, 'Escolha um <b>Host-Group:</b>', reply_markup=menu,parse_mode="HTML")

#LIDA COM OS CALLBACKS DAS PAGINAS
@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def callback_paginas(call):

    chat_id = call.message.chat.id
    source = call.data.split(',')
    data = source[0]
    data_extraida = data.split('_')
    pagina = int(data_extraida[1])
    prefixo = source[1]
    items_por_pagina = 8


    #CRIA UM MENU PAGINADO DOS HOST_GROUPS
    if prefixo == "hgroup":
    
        

        #AGRUPA EM UMA  LISTA OS NOMES DOS HOST GROUP PARA CRIAR OS BOTÕES PAGINADOS
        paginas = Paginacao(list(users[chat_id].grupos_dict.values()))

        menu = paginas.criar_pagina(pagina, items_por_pagina,prefixo)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                            text='Escolha um <b>Host-Group:</b>', reply_markup=menu,parse_mode="HTML")
    
    #CRIA UM MENU PAGINADO DOS HOSTS
    if prefixo == "host":
        

        #AGRUPA EM UMA  LISTA OS NOMES DOS HOST GROUP PARA CRIAR OS BOTÕES PAGINADOS
        paginas = Paginacao(list(users[chat_id].host_graph_agrupados.keys()))

        menu_host = paginas.criar_pagina(pagina, items_por_pagina,prefixo)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                            text='Escolha um <b>Host:</b>', reply_markup=menu_host,parse_mode="HTML")
        
    #CRIA UM MENU PAGINADO DOS HOSTS
    if prefixo == "items":
        items_por_pagina = 8

        #AGRUPA EM UMA  LISTA OS NOMES DOS HOST GROUP PARA CRIAR OS BOTÕES PAGINADOS
        paginas = Paginacao(list(users[chat_id].graph_item.keys()))

        menu_item = paginas.criar_pagina(pagina, items_por_pagina,prefixo)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                            text='Escolha um <b>Item:</b>', reply_markup=menu_item,parse_mode="HTML")
        
    




@bot.callback_query_handler(func=lambda call:call.data in users[call.message.chat.id].grupos_dict.values())
def callbacks_host(call):


    chat_id = call.message.chat.id
    pagina = 1
    items_por_pagina = 8
    prefixo = "host"

    #EVITA DUPLICIDADE DE BOTÕES
    users[chat_id].host_graph_agrupados = {}

    
    list_ids = []
    for id,group_name in users[chat_id].grupos_dict.items():
        if call.data ==group_name:
            list_ids.append(id)
        
    graphs_get = users[chat_id].zapi.graph.get({
        'output':['graphid'],
        'groupids':list_ids,
        'selectHosts':['name'],
        'selectItems':['name']

    })

    #ID DO GRÁFICO COM O NOME DO HOST
    graph_id_hosts = {graph_id['graphid']:graph_id['hosts'][0]['name'] for graph_id in graphs_get}

    #ID DO GRAFICO COM NOME DO ITEM
    users[chat_id].item_name_graph = {item['graphid']:item['items'][0]['name'] for item in graphs_get}
    
    
    for id_graph,h_name in graph_id_hosts.items():
        if h_name not in users[chat_id].host_graph_agrupados:
            users[chat_id].host_graph_agrupados[h_name] = []
        if id_graph not in users[chat_id].host_graph_agrupados[h_name]:
            users[chat_id].host_graph_agrupados[h_name[:50]].append(id_graph)


    
    paginas = Paginacao(list(users[chat_id].host_graph_agrupados.keys()))
    menu_host = paginas.criar_pagina(pagina,items_por_pagina,prefixo)

    bot.send_message(chat_id,"Selecione um <b>Host</b> para exibir os Gráficos:",reply_markup=menu_host,parse_mode="HTML")

    
@bot.callback_query_handler(func=lambda call:call.data if call.data in users[call.message.chat.id].host_graph_agrupados  else False)
def callbacks_item(call):
    chat_id = call.message.chat.id
    users[chat_id].graph_item = {}
    print(f'HOST {call.data}')

    pagina = 1
    items_por_pagina = 8
    prefixo = "items"

    
    for n_host,g_ids in users[chat_id].host_graph_agrupados.items():
        for ids in g_ids:
            for graph_id_item,item_name in users[chat_id].item_name_graph.items():
                if call.data == n_host:
                    if ids == graph_id_item:
                        users[chat_id].graph_item[item_name[:50]] = ids
 

    

    items = Paginacao(list(users[chat_id].graph_item.keys()))
    menu_item = items.criar_pagina(pagina,items_por_pagina,prefixo)

    print(users[call.message.chat.id].graph_item)

    bot.send_message(chat_id,f"Selecione um item do host:\n <b>{call.data}</b> ",reply_markup=menu_item,parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in users[call.message.chat.id].graph_item.keys())
def callbacks_graphs(call):
    

    print(f'CALL DATA : {call.data}')

    
    chat_id = call.message.chat.id
    users[chat_id].id_grafico = ""

    for i_name,g_id in users[chat_id].graph_item.items():
        print(f'NOME DO GRAFICO : {i_name}')
        if call.data == i_name:
            users[chat_id].id_grafico = g_id

            menu_periodo = types.InlineKeyboardMarkup()
            botoes_periodo = []
            botoes_periodo.append(types.InlineKeyboardButton(f"{periodo_3} 3 Horas ",callback_data="horas_3"))
            botoes_periodo.append(types.InlineKeyboardButton(f"{periodo_6} 6 Horas ",callback_data="horas_6"))
            botoes_periodo.append(types.InlineKeyboardButton(f"{periodo_9} 9 Horas ",callback_data="horas_9"))
            botoes_periodo.append(types.InlineKeyboardButton(f"{periodo_12} 12 Horas ",callback_data="horas_12"))
            menu_periodo.row(*botoes_periodo)

            bot.send_message(chat_id,"Escolha um periodo para criação do gráfico",reply_markup=menu_periodo)

    
#VERIFICA OS CALLBACKS DOS BOTÕES DE PERIODOS
@bot.callback_query_handler(func=lambda call: call.data.startswith("horas"))
def callbacks_graphs(call):
    print(call.data)
    
    chat_id = call.message.chat.id

    if call.data == "horas_3":
        for i_name,g_id in users[chat_id].graph_item.items():
            if g_id == users[chat_id].id_grafico:
                grafico_zabbix_3h = gerar_grafico(g_id,3)
                bot.send_message(chat_id,f"Segue a imagem do gráfico:\n<b>{i_name}</b>\n no periodo de:\n <b>3 horas</b>:",parse_mode="HTML")
                bot.send_photo(chat_id,photo=open(grafico_zabbix_3h,"rb"))
              
                
    if call.data == "horas_6":
        for i_name,g_id in users[chat_id].graph_item.items():
            if g_id == users[chat_id].id_grafico:
                grafico_zabbix_6h = gerar_grafico(g_id,6)
                bot.send_message(chat_id,f"Segue a imagem do gráfico:\n<b>{i_name}</b>\n no periodo de:\n <b>6 horas</b>:",parse_mode="HTML")
                bot.send_photo(chat_id,photo=open(grafico_zabbix_6h,"rb"))


    if call.data == "horas_9":
        for i_name,g_id in users[chat_id].graph_item.items():
            if g_id == users[chat_id].id_grafico:
                grafico_zabbix_9h = gerar_grafico(g_id,9)
                bot.send_message(chat_id,f"Segue a imagem do gráfico:\n<b>{i_name}</b>\n no periodo de:\n <b>9 horas</b>:",parse_mode="HTML")
                bot.send_photo(chat_id,photo=open(grafico_zabbix_9h,"rb"))


    if call.data == "horas_12":
        for i_name,g_id in users[chat_id].graph_item.items():
            if g_id == users[chat_id].id_grafico:
                grafico_zabbix_12h = gerar_grafico(g_id,12)
                bot.send_message(chat_id,f"Segue a imagem do gráfico:<b>\n{i_name}</b>\n no periodo de:\n <b>12 horas</b>:",parse_mode="HTML")
                bot.send_photo(chat_id,photo=open(grafico_zabbix_12h,"rb"))



            
            
           
            
            

        
@bot.message_handler(commands=['ajuda','start'])
def ajuda(message):
    usu = message.from_user.first_name
    bot.send_message(
        message.chat.id,
(f'''Ola <b>{usu}</b>{e_ola}
Para utilizar as funções do <b>Zabbix</b> basta digitar:

/inicio
 
Assim será solicitado seu <b>Login</b> e sua <b>Senha</b>

Após a validação do login, você pode escolher:
 
<b>Reconhecimento</b>{e_certo} 
<b>Buscar os Gráficos</b>{e_graph}

Em breve teremos mais funções!

Obrigado
'''
        ),parse_mode="HTML")




    
                



bot.polling(non_stop=True)
