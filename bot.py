#!/usr/bin/python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
import sys
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, ChatAction, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import filecmp
import datetime
import difflib

# Habilitar el logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Parámetros de la URL a monitorizar, el chat_id sobre el que enviar avisos y el token de desarrollador para el BOT
url = 'https://www.url_to_track_changes.com/'
chat_id = '123456789'
token = '123456789:AAEAA_AAA-A-AAAAAAAAAAAAAAAAAAAAAAA'

# Método de inicio del Bot y el mensaje de bienvenida
def start(bot, update):
    update.message.reply_text("Hola, este bot te avisa cuando cambia la web que se trackea")

# Método de /help para comprobar desde el móvil si el bot sigue vivo
def hola(bot, update):
    update.message.reply_text("hola que ase, sigues vivo o que ase")

# Este método hace un get de la URL a monitorizar y lo guarda sobre el fichero second.txt
def get_url(bot, job):

    try:
        # Se realiza un get sobre la URL y nos quedamos con .content, un string con el contenido html de la web
        result_current = requests.get(url)
        c_current = result_current.content
        # Se eliminan los últimos 174 caracteres que son la marca de fecha y tiempo que incluye el request.get
        c_current = c_current[:-174]
    except requests.exceptions.HTTPError as e:
        add_log_message("Error en el método get_url en request.get " + str(e))
        print ("Error en el método get_url en request.get " + str(e))

    # Se actualiza el contenido del fichero second.txt
    try:
        save_2 = open("second.txt","wb+")
        save_2.write(c_current)
        save_2.close()
    except IOError:
        add_log_message("Error en el método get_url refrescando el contenido de second.txt")
        print ("Error en el método get_url refrescando el contenido de second.txt")

def check_n_notify(bot, job):

    if not filecmp.cmp('first.txt', 'second.txt'):
        try:
            save_2 = open("second.txt", "rb+") 
            c_current = save_2.read()

            save_to_compare_2 = open("second_compare.txt", "wb+")
            save_to_compare_2.write(c_current)
            save_to_compare_2.close()

            save_1_comp = open("first.txt", "rb+") 
            c_comp = save_1_comp.read()
            save_to_compare_1 = open("first_compare.txt", "wb+")
            save_to_compare_1.write(c_comp)
            save_to_compare_1.close()
        except IOError:
            add_log_message("Error en check_n_notify abriendo el fichero second.txt")
            print ("Error en check_n_notify abriendo el fichero second.txt")
        
        try:
            save = open("first.txt","wb+")
            save.write(c_current)
            save.close()
        except IOError:
            add_log_message("Error en check_n_nofify durante la actualización del fichero first.txt")
            print ("Error en check_n_nofify durante la actualización del fichero first.txt")

        try:
            save1 = open("first_compare.txt", "r") 
            comp = save1.read()
            save2 = open("second_compare.txt", "r")
            comp2 = save2.read()
        except IOError:
            add_log_message("Error en la lectura de ficheros para el envio al usuario de las diferencias encontradas")
            print ("Error en el envio al usuario de las diferencias encontradas")

        diferencia = ""
        for line in difflib.context_diff(comp, comp2):
            diferencia = diferencia + line
        
        msg = "LA WEB HA CAMBIADO!!!\r\n" + diferencia

        # Envía un mensaje al usuario, la web ha cambiado!
        bot.send_message(chat_id=chat_id, text=msg)

def send_alive(bot, job):
    bot.send_message(chat_id=chat_id, text='Ey, que sigo vivo!')

def error(bot, update, error):
    add_log_message("Algo ha explotado " + str(update) + " " + str(error))
    logger.warning('Algo ha explotado', update, error)

def add_log_message(msg):
    # Añadimos entrada en  el fichero de log
    try:
        save_log = open("log.txt","a+")
        save_log.write(get_time() + msg + "\r\n")
        save_log.close()
    except IOError:
        print ("Error con el fichero log.txt")

def get_time():
    now = datetime.datetime.now()
    return (str(now.day) + "/" + str(now.month) + "/" + str(now.year) + " - " + str(now.hour) + ":"  + str(now.minute)+ ":"  + str(now.second) + " - ")

def main():

    try:
        # Se almacena el estado inicial de la web en el fichero first.txt
        result = requests.get(url)
        c = result.content
        c = c[:-174]
    except requests.exceptions.HTTPError as e:
        add_log_message("Error en el get para crear el fichero first.txt " + str(e))
        print ("Error en el get para crear el fichero first.txt " + str(e))

    try:
        save_1 = open("first.txt","wb+")
        save_1.write(c)
        save_1.close()
    except IOError:
        add_log_message("Error en la creación del fichero first.txt")
        print ("Error en la creación del fichero first.txt")

    # Se inicia el BOT
    updater = Updater(token)

    # Se inicia el timer que comprueba si la web ha cambiado
    j = updater.job_queue
    job = j.run_repeating(check_n_notify, interval=60, first=20)

    # Se inicia el timer que actualiza second.txt con el estado actual de la web
    job_2 = j.run_repeating(get_url, interval=60, first=0)

    # Se inicia el timer que refresca el estado cada 2 horas
    job_3 = j.run_repeating(send_alive, interval=7200, first=0)

    # Se crea el dispatcher para registrar handlers de usuario
    dp = updater.dispatcher
    # Diferentes handlers para los comnandos del usuario
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('hola', hola))
    dp.add_error_handler(error)

    # Se arranca el bot
    updater.start_polling()

    add_log_message("Starting bot ....")

    updater.idle()

if __name__ == '__main__':
    main()
