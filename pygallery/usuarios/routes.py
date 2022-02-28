from array import array
import os
import json
from urllib import response
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, abort, session, jsonify, make_response
from flask_login import login_user, current_user, logout_user, login_required
from pygallery import db, bcrypt
from hashlib import md5
from pygallery.models import Usuario, Etiqueta, Imagen, Users, Events
from pygallery.usuarios.utils import math_all, math_plus, allowed_file, generate_string
from pygallery import login_manager
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image
from os.path import join, dirname, realpath
import pdfkit

usuarios = Blueprint('usuarios', __name__)
UPLOAD_FOLDER = '/static/uploads/avatar'


@login_manager.unauthorized_handler
def unauthorized_callback():
    print('Не авторизирован')
    return redirect('/login')


@login_manager.user_loader
def load_user(user_id):
    # print("Сессия пользователя активна")
    return Users.query.get(int(user_id))


@usuarios.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('usuarios.profile'))
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        curr_user = Users.query.filter_by(email=email).first()
        if curr_user:
            hashpass = md5(password.encode('utf-8'))
            md5_hashpass = hashpass.hexdigest()
            if md5_hashpass == curr_user.password:
                login_user(curr_user)
                session["id"] = curr_user.id
                return redirect(url_for("usuarios.profile"))
            else:
                flash("Неверная пара логина и пароля!", category='danger')
                return redirect(url_for("usuarios.login"))
        else:
            flash("Пользователя с таким эмейлом не существует!", category='danger')
            return redirect(url_for("usuarios.login"))
    return render_template('login.html')


@usuarios.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('usuarios.profile'))
    if request.method == 'POST':
        if Users.query.filter(Users.email == request.form['email']).first():
            flash('Пользователь с таким эмейл уже существует!', category='danger')
            return redirect(url_for("usuarios.register"))
        elif not request.form['username'] or not request.form['firstname'] or not request.form['lastname'] or not request.form['email'] or not request.form['password'] or not request.form['level'] or not request.form['uzname']:
            flash('Заполнены не все поля', category='danger')
            return redirect(url_for("usuarios.register"))
        else:
            if (request.form['level'] == '0' or request.form['level'] == '1') and (request.form['uzname'] == 'СГСПУ'):
                username = request.form['username']
                firstname = request.form['firstname']
                lastname = request.form['lastname']
                email = request.form['email']
                password = request.form['password']
                confirmpassword = request.form['confirmpassword']
                if password == confirmpassword:
                    level = request.form['level']
                    uzname = request.form['uzname']
                    hashpass = md5(password.encode('utf-8'))
                    md5_hashpass = hashpass.hexdigest()
                    created_on = datetime.today().strftime('%Y-%m-%d')
                    newUser = Users(username=username, firstname=firstname, lastname=lastname, email=email, uzname=uzname,
                                    level=level, password=md5_hashpass, department='department', avatar='none.jpg', created_on=created_on)
                    db.session.add(newUser)
                    db.session.commit()
                    flash('Поздравляем с успешной регистрацией',
                          category='success')
                    return redirect(url_for("usuarios.login"))
                else:
                    flash('Пароли не совпадают', category='danger')
                    return redirect(url_for("usuarios.register"))
            flash('Ошибка введенных данных', category='danger')
            return redirect(url_for("usuarios.register"))
    return render_template('register.html')


@usuarios.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@usuarios.route("/profile")
@login_required
def profile():
    data_math = math_plus(current_user.id)
    data_math_all = math_all(data_math)
    level_array = ['Неподтвержденный пользователь', 'Студент', 'Профорг',
                   'Председатель профбюро факультета', 'Председатель ППОС', 'Управляющий']
    me = Users.query.filter_by(id=current_user.id).first_or_404()
    return render_template('profile.html', me=me, level_array=level_array, data=data_math, data2=data_math_all)


@usuarios.route("/profile/settings")
@login_required
def profile_settings():
    DEPARTMENT = [
        ['СГСПУ-1', 'ФМФИ', 'Факультет математики, физики и информатики'],
        ['СГСПУ-2', 'ФПСО', 'Факультет психологии и специального образования'],
        ['СГСПУ-3', 'ФКИ', 'Факультет культуры и искусства'],
        ['СГСПУ-4', 'ИФ', 'Исторический факультет'],
        ['СГСПУ-5', 'ФФ', 'Филологический факультет'],
        ['СГСПУ-6', 'ФИЯ', 'Факультет иностранных языков'],
        ['СГСПУ-7', 'ФЭУС', 'Факультет экономики, управления и сервиса'],
        ['СГСПУ-8', 'ФФКиС', 'Факультет физической культуры и спорта'],
        ['СГСПУ-9', 'ФНО', 'Факультет начального образования'],
        ['СГСПУ-10', 'ЕГФ', 'Естественно-географический факультет'],
    ]
    data_math = math_plus(current_user.id)
    me = Users.query.filter_by(id=current_user.id).first_or_404()
    return render_template('profile/settings.html', me=me, data=data_math, array_department=DEPARTMENT)


@usuarios.route("/user/<int:id>")
@login_required
def user(id):
    level_array = ['Незарегистрирован', 'Пользователь', 'Профорг',
                   'Председатель профбюро факультета', 'Председатель ППОС', 'Управляющий']
    user = Users.query.filter_by(id=id).first_or_404()
    me = Users.query.filter_by(id=current_user.id).first_or_404()
    return render_template('user.html', me=me, user=user, level_array=level_array)


@usuarios.route("/users")
@login_required
def users():
    me = Users.query.filter_by(id=current_user.id).first_or_404()
    return render_template('users.html', me=me)


@usuarios.route('/get_data', methods=['POST'])
def get_data_function():
    userSearch = request.form['userSearch']
    cursorQuery = (
        f"(SELECT id, username, firstname, lastname, email, uzname, level, department, avatar, created_on FROM public.users WHERE lastname ILIKE '%{userSearch}%')")
    cur = db.session.execute(cursorQuery)
    records = cur.fetchall()
    insertObject = []
    c = db.session.execute(
        "select column_name from information_schema.columns where table_schema = 'public' and table_name='users'")
    column_names = [row[0] for row in c]
    column_names.remove('password')
    for record in records:
        insertObject.append(dict(zip(column_names, record)))
    for element in insertObject:
        element.pop('username')
        element.pop('uzname')
        element.pop('department')
        element.pop('avatar')
        element.pop('created_on')
    return json.dumps(insertObject, indent=4, default=str)


@usuarios.route('/update_photo', methods=['GET', 'POST'])
@login_required
def update_photo():
    if request.method == 'POST':
        if 'upload_photo' in request.form:
            if 'photo' not in request.files:
                flash('Нет файловой части', category='danger')
                return redirect(url_for("usuarios.profile_settings"))
            file = request.files['photo']
            if file.filename == '':
                flash('Файл не выбран', category='danger')
                return redirect(url_for("usuarios.profile_settings"))
            try:
                if file and allowed_file(file.filename):
                    extension = secure_filename(
                        file.filename).rsplit('.', 1)[1]
                    new_file_name = generate_string(16)
                    image_name_file = new_file_name + '.' + extension
                    image_path = os.path.join(
                        current_app.root_path, 'static/uploads/avatar/' + image_name_file)
                    file.save(image_path)
                    db.session.execute(
                        f"UPDATE users SET avatar = '{image_name_file}' WHERE id = {current_user.id};")
                    db.session.commit()
                    # db.user.update_one({"_id": str(current_user.id), {"$set": {"avatar": path}})
                    flash('Фотография успешно обновленна', category='success')
                    return redirect(url_for("usuarios.profile_settings"))
                else:
                    flash('Недопустимое расширение файла', category='danger')
                    return redirect(url_for("usuarios.profile_settings"))
            except Exception as e:
                print(e)
                flash('Ошибка загрузки файла', category='danger')
                return redirect(url_for("usuarios.profile_settings"))


@usuarios.route('/get_pgas', methods=['GET', 'POST'])
@login_required
def get_pgas():
    action = request.form['action']
    if request.method == 'POST' and action == "get_pgas":
        cursorQuery = (f"SELECT u.lastname, u.firstname, u.department, ev.name, e.memberrole, e.nagrada FROM public.eventship as e  INNER JOIN users as u ON e.memberid = u.id INNER JOIN events as ev ON ev.link = e.eventlink WHERE e.memberid = {current_user.id} AND e.nagrada = 1;")
        cur = db.session.execute(cursorQuery)
        records = cur.fetchall()
        data = []
        for p in records:
            data.append({
                'lastname': p.lastname,
                'firstname': p.firstname,
                'department': p.department,
                'name': p.name,
                'memberrole': p.memberrole,
                'nagrada': p.nagrada
            })
        resp = jsonify(data)
        res = render_template('pgas.html')
        responsestring = pdfkit.from_string(res, False)
        response = make_response(responsestring)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline;filename=pgas.pdf'
        return response


