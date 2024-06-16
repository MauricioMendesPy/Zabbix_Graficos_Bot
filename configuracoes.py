#---------------------------------------------------------------------------------------------#
#                          Arquivo de configurações para o funcionamento do Bot               #         
#                                  Modifique conforme sua necessidade                         #              
#                                           Desenvolvido por:                                 #
#                                            Mauricio Mendes                                  #
#                                      Github - MauricioMendesPy                              #                          
#                                                                                             #
#                                                                                             #
#                                                                                             #
#-----------------------------------------------------------------------------------------------
from telebot import TeleBot,types




#CONFIGURAÇÕES DO TELEGRAM----------------------------------------------#
api_token = "TOKEN DO SEU BOT"
bot = TeleBot(api_token)
#ZABBIX------------------------------------------------------------------#
url_zab = "URL DO SEU ZABBIX"
user_admin = "LOGIN ADMIN"
senha_admin = "SENHA ADMIN"


#SE SUA PAGINA DE LOGIN ESTIVER EM INGLÊS , MUDE PARA "US"
lang_front = "PT"

################################################ EMOJIS ######################################################

e_certo = "✅"
e_mensagem = "✉"
e_sirene = "🚨"
e_graph = "📉"
e_ola = "👋"
e_atencao = "⚠"
e_check_box = "☑"
periodo_3 = "🕒"
periodo_6 = "🕕"
periodo_9 = "🕘"
periodo_12 = "🕛"








