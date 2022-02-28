import os
from flask import Blueprint, request, render_template, redirect, url_for, send_from_directory, current_app
from flask_login import current_user
from pygallery.models import Imagen

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('usuarios.profile'))
    return render_template('index.html')

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')