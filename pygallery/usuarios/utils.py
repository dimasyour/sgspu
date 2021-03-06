import os

from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from pygallery import mail, db
import string
import random


def enviar_mail(usuario):
    token = usuario.get_reset_token()
    msg = Message('Solicitud de reestablecimiento de Contraseña',
                  sender='noreply@pygallery.com', recipients=[usuario.email])
    msg.body = f''' Para reestablecer tu contraseña visita el siguiente enlace:
{url_for('usuarios.reestablecer_contraseña', token = token, _external=True)}
Si no hiciste esta solicitud simplemente ignora este mensaje y no se hara ningún cambio.
'''
    mail.send(msg)


def math_plus(own):
    sfera_array = ['Общественная', 'Творческая', 'Спортивная', 'Научная']
    status_array = [0, 1, 2]
    result = []
    for sfera in range(len(sfera_array)):
        result.append([])
        result[sfera].append(sfera_array[sfera])
        for status in range(len(status_array)):
            cursor = db.session.execute(
                f"SELECT count(*) FROM public.events WHERE own = {own} AND sfera = '{sfera_array[sfera]}' AND status = {status}")
            result[sfera].append(cursor.fetchone()[0])
    sum_event = 0
    for i in range(len(result)):
        for j in range(len(result[i])):
            if result[i][j] != 0 and j != 0:
                sum_event = sum_event + result[i][j]
        result[i].append(sum_event)
        sum_event = 0
    return result


def math_all(Arr):
    sum_success = 0
    sum_progressing = 0
    sum_cancel = 0
    for i in Arr:
        sum_progressing = sum_progressing + i[1]
        sum_success = sum_success + i[2]
        sum_cancel = sum_cancel + i[3]
    result = [sum_progressing, sum_success, sum_cancel]
    return result


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}


def generate_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string
