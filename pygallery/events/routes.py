from array import array
import os
import json
from unicodedata import category
from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, abort, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from pygallery import db, bcrypt
from hashlib import md5
from pygallery.models import Usuario, Etiqueta, Imagen, Users, Events, Event, Eventship
from pygallery.usuarios.utils import math_all, math_plus, allowed_file, generate_string
from pygallery import login_manager
from datetime import datetime, timezone
import datetime
events = Blueprint('events', __name__)

dt = datetime.datetime.today()

SFERA_EVENT = ['Общественная','Творческая', 'Научная', 'Спортивная']

@events.route('/events/add_event', methods=['GET', 'POST'])
@login_required
def events_add_event():
    if 'add_event' in request.form and request.method == 'POST':
        name = request.form['name']
        sfera = request.form['sfera']
        level = int(request.form['level'])
        seats = int(request.form['seats'])
        datestart = request.form['datestart']
        dateend = request.form['dateend']
        dateregstart = request.form['dateregstart']
        dateregend = request.form['dateregend']
        dop = request.form['dop']
        link = generate_string(16)
        if current_user.level < 3 and level == 1:
            newEvent = Events(name=name, sfera=sfera, level=level, seats=seats, datestart=datestart, own=current_user.id,
                              dateend=dateend, dateregstart=dateregstart, dateregend=dateregend, moderator=3, status=0, link=link, dop=dop)
            flash('Мероприятие добавлено в обработку', category='success')
        elif current_user.level < 3 and level == 2:
            newEvent = Events(name=name, sfera=sfera, level=level, seats=seats, datestart=datestart, own=current_user.id,
                              dateend=dateend, dateregstart=dateregstart, dateregend=dateregend, moderator=4, status=0, link=link, dop=dop)
            flash('Мероприятие добавлено в обработку', category='success')
        elif current_user.level == 3 and level == 1:
            newEvent = Events(name=name, sfera=sfera, level=level, seats=seats, datestart=datestart, own=current_user.id,
                              dateend=dateend, dateregstart=dateregstart, dateregend=dateregend, moderator=3, status=1, link=link, dop=dop)
            newEventship = Eventship(eventlink=link, memberid=current_user.id, memberrole=1, nagrada=0)
            db.session.add(newEvent)
            db.session.commit()
            db.session.add(newEventship)
            db.session.commit()
            flash('Мероприятие добавлено и принято', category='success')
        elif current_user.level == 3 and level == 2:
            newEvent = Events(name=name, sfera=sfera, level=level, seats=seats, datestart=datestart, own=current_user.id,
                              dateend=dateend, dateregstart=dateregstart, dateregend=dateregend, moderator=4, status=0, link=link, dop=dop)
            flash('Мероприятие добавлено в обработку', category='success')
        elif current_user.level > 3 and level <= 2:
            newEvent = Events(name=name, sfera=sfera, level=level, seats=seats, datestart=datestart, own=current_user.id,
                              dateend=dateend, dateregstart=dateregstart, dateregend=dateregend, moderator=4, status=1, link=link, dop=dop)
            newEventship = Eventship(eventlink=link, memberid=current_user.id, memberrole=1, nagrada=0)
            db.session.add(newEvent)
            db.session.commit()
            db.session.add(newEventship)
            db.session.commit()
            flash('Мероприятие добавлено и принято', category='success')
        else:
            print('Ошибка добавления мероприятия!')
            redirect(url_for("add_event"))
        db.session.add(newEvent)
        db.session.commit()
        return redirect(url_for("usuarios.profile"))
    else:
        me = Users.query.filter_by(id=current_user.id).first_or_404()
        return render_template('events/add_event.html', me=me)


@events.route('/events/my', methods=['GET', 'POST'])
@login_required
def events_my():
    me = Users.query.filter_by(id=current_user.id).first_or_404()
    return render_template('events/my.html', me=me)


@events.route('/get_my_events', methods=['POST'])
def get_my_events():
    eventSearch = request.form['eventSearch']
    status = request.form['status']
    if status == "all":
        cursorQuery = (
            f"(SELECT name, datestart, dateend, status, link FROM public.events WHERE name ILIKE '%{eventSearch}%' AND own = {current_user.id})")
    elif status == "ob":
        cursorQuery = (
            f"(SELECT name, datestart, dateend, status, link FROM public.events WHERE name ILIKE '%{eventSearch}%' AND status = 1 OR status = 2 AND own = {current_user.id})")
    elif status == "neob":
        cursorQuery = (
            f"(SELECT name, datestart, dateend, status, link FROM public.events WHERE name ILIKE '%{eventSearch}%' AND status = 0 AND own = {current_user.id})")
    else:
        cursorQuery = (
            f"(SELECT name, datestart, dateend, status, link FROM public.events WHERE name ILIKE '%{eventSearch}%' AND status = {status} AND own = {current_user.id})")
    cur = db.session.execute(cursorQuery)
    records = cur.fetchall()
    insertObject = []
    c = db.session.execute(
        "select column_name from information_schema.columns where table_schema = 'public' and table_name='events'")
    column_names = [row[0] for row in c]
    column_names.remove('id')
    column_names.remove('sfera')
    column_names.remove('level')
    column_names.remove('seats')
    column_names.remove('dateregstart')
    column_names.remove('dateregend')
    column_names.remove('own')
    column_names.remove('moderator')
    column_names.remove('dop')
    for record in records:
        insertObject.append(dict(zip(column_names, record)))
    return json.dumps(insertObject, indent=4, default=str)


@events.route("/event/<string:link>")
@login_required
def event_enroll(link):
    event = Events.query.filter_by(link=link).first_or_404()
    me = Users.query.filter_by(id=current_user.id).first_or_404()
    return render_template('events/event.html', me=me, event=event)


@events.route("/event/enroll/<string:link>", methods=['GET', 'POST'])
@login_required
def event_view(link):
    if request.method == 'POST':
        solution = request.form['action']
        if solution == 'event_end':
            cursorQuery = (f"UPDATE eventship SET nagrada = case WHEN eventlink = '{link}' THEN 1 else nagrada end;")
            db.session.execute(cursorQuery)
            db.session.commit()
            cursorQuery2 = (f"UPDATE public.events SET status = 3 WHERE link = '{link}';")
            db.session.execute(cursorQuery2)
            db.session.commit()
            flash('Мероприятие успешно завершенно', category='success')
            return redirect(url_for('events.calend'))
    cursorQuery2 = (f"SELECT COUNT(*) FROM eventship WHERE eventlink = '{link}'")
    cur2 = db.session.execute(cursorQuery2)
    zanyato = int(cur2.fetchone()[0])
    event = Events.query.filter_by(link=link).first_or_404()
    me = Users.query.filter_by(id=current_user.id).first_or_404()
    cursorQuery = (f"SELECT id, firstname, lastname, memberrole FROM users JOIN eventship ON eventship.eventlink = '{link}' and eventship.memberid = users.id")
    cur = db.session.execute(cursorQuery)
    records = cur.fetchall()
    return render_template('events/enroll.html', me=me, event=event, members=records, zanyato=zanyato)


@events.route("/e_<string:link>", methods=['GET', 'POST'])
@login_required
def event_link(link):
    eventship = Eventship.query.filter(Eventship.eventlink == link).filter(Eventship.memberid == current_user.id)
    if request.method == 'POST':
        solution = request.form['solution']
        if solution == 'plus':
            if eventship.filter(Eventship.memberrole == 1).first():
                flash('Вы являетесь организатором и не можете понизиться до участника', category='danger')
                return redirect(url_for("events.calend"))
            elif eventship.filter(Eventship.memberrole == 2).first():
                flash('Вы уже участвуйте в этом мероприятии', category='danger')
                return redirect(url_for("events.calend"))
            event = Events.query.filter_by(link=link).first_or_404()
            cursorQuery2 = (f"SELECT COUNT(*) FROM eventship WHERE eventlink = '{link}'")
            cur2 = db.session.execute(cursorQuery2)
            zanyato = int(cur2.fetchone()[0])
            if not eventship.filter(Eventship.memberid == current_user.id).first() and event.seats - zanyato > 0:
                newEventship = Eventship(eventlink=link, memberid=current_user.id, memberrole=2, nagrada=0)
                db.session.add(newEventship)
                db.session.commit()
            if event.seats - zanyato > 0:
                cursorQuery = (f"UPDATE eventship SET memberrole = 2 WHERE eventlink = '{link}' AND memberid = {current_user.id};")
                db.session.execute(cursorQuery)
                db.session.commit()
                flash('Вы успешно записались на мероприятие', category='success')
                return redirect(url_for("events.calend"))
            else:
                flash('Места на это мероприятие закончились', category='danger')
                return redirect(url_for("events.calend"))
        elif solution == 'minus':
            if Eventship.query.filter(Eventship.eventlink == link).filter(Eventship.memberid == current_user.id).filter(Eventship.memberrole == 1).first():
                flash('Вы являетесь организатором и не можете отказаться от участия', category='danger')
                return redirect(url_for("events.calend"))
            cursorQuery = (f"UPDATE eventship SET memberrole = 0 WHERE eventlink = '{link}' AND memberid = {current_user.id};")
            db.session.execute(cursorQuery)
            db.session.commit()
            flash('Вы снялись с участия в мероприятии', category='warning')
            return redirect(url_for("events.calend"))
    me = Users.query.filter_by(id=current_user.id).first_or_404()
    cursorQuery = (f"(Select e.name, e.sfera, e.level, e.seats, e.datestart, e.dateend, e.dateregstart, e.dateregend, e.status, e.link, e.dop, u.id, u.firstname, u.lastname From events e Join users u ON e.own = u.id WHERE e.link = '{link}')")
    cur = db.session.execute(cursorQuery)
    event = cur.fetchall()[0]
    if eventship.filter(Eventship.memberrole == 2).first():
        return render_template('events/eventForMember.html', me=me, event=event, array_sfera=SFERA_EVENT)
    if eventship.filter(Eventship.memberrole == 1).first():
        return redirect(url_for('events.event_view', link=link))
    return render_template('events/eventForNotMember.html', me=me, event=event, array_sfera=SFERA_EVENT)


@events.route("/events/manage")
@login_required
def events_manage():
    if current_user.level >= 3:
        me = Users.query.filter_by(id=current_user.id).first_or_404()
        return render_template('events/manage.html', me=me)
    else:
        return redirect(url_for('usuarios.profile'))


@events.route("/event/manage/<string:link>", methods=['GET', 'POST'])
@login_required
def event_manage(link):
    if request.method == 'POST':
        solution = request.form['solution']
        if solution == 'agree':
            db.session.execute(
                f"UPDATE events SET status = 1 WHERE link = '{link}';")
            db.session.commit()
            event = Events.query.filter_by(link=link).first_or_404()
            newEventship = Eventship(
                eventlink=link, memberid=event.own, memberrole=1, nagrada=0)
            db.session.add(newEventship)
            db.session.commit()
            flash('Мероприятие принято', category='warning')
            return redirect(url_for("events.events_manage"))
        elif solution == 'backEnroll':
            db.session.execute(
                f"UPDATE events SET status = 0 WHERE link = '{link}';")
            db.session.commit()
            flash('Мероприятие возвращено в обработку', category='warning')
            return redirect(url_for("events.events_manage"))
        elif solution == 'disagree':
            db.session.execute(
                f"UPDATE events SET status = 2 WHERE link = '{link}';")
            db.session.commit()
            flash('Мероприятие отклоненно', category='warning')
            return redirect(url_for("events.events_manage"))
        else:
            flash('Произошла ошибка обновления статуса заявки', category='danger')
            return redirect(url_for("events.events_manage"))
    else:
        me = Users.query.filter_by(id=current_user.id).first_or_404()
        cursorQuery = (f"(Select e.name, e.sfera, e.level, e.seats, e.datestart, e.dateend, e.dateregstart, e.dateregend, e.status, e.link, e.dop, u.id, u.firstname, u.lastname From events e Join users u ON e.own = u.id WHERE e.link = '{link}')")
        cur = db.session.execute(cursorQuery)
        event = cur.fetchall()[0]
        array_sfera = ['Общественная', 'Творческая', 'Научная', 'Спортивная']
        return render_template('events/manage_event.html', me=me, event=event, array_sfera=array_sfera)


@events.route('/get_request_events', methods=['POST'])
def get_request_events():
    if current_user.level >= 3:
        if current_user.level == 3:
            moder_level = '(e.moderator = 3)'
        elif current_user.level == 4:
            moder_level = '(e.moderator = 3 OR e.moderator = 4)'
        enrollSearch = request.form['enrollSearch']
        status = request.form['status']
        if status == "all":
            cursorQuery = (
                f"(SELECT e.name, e.datestart, e.dateregstart, u.lastname, u.firstname, e.link, u.id, e.status FROM events AS e JOIN users AS u ON u.id = e.own WHERE name ILIKE '%{enrollSearch}%' AND {moder_level} ORDER BY e.datestart DESC)")
        elif status == "ob":
            cursorQuery = (
                f"(SELECT e.name, e.datestart, e.dateregstart, u.lastname, u.firstname, e.link, u.id, e.status FROM events AS e JOIN users AS u ON u.id = e.own WHERE name ILIKE '%{enrollSearch}%' AND e.status = 1 OR e.status = 2 AND {moder_level}  ORDER BY e.datestart DESC)")
        elif status == "neob":
            cursorQuery = (
                f"(SELECT e.name, e.datestart, e.dateregstart, u.lastname, u.firstname, e.link, u.id, e.status FROM events AS e JOIN users AS u ON u.id = e.own WHERE name ILIKE '%{enrollSearch}%' AND e.status = 0 AND {moder_level}  ORDER BY e.datestart DESC )")
        else:
            cursorQuery = (
                f"(SELECT e.name, e.datestart, e.dateregstart, u.lastname, u.firstname, e.link, u.id, e.status FROM events AS e JOIN users AS u ON u.id = e.own WHERE name ILIKE '%{enrollSearch}%' AND e.status = {status} AND {moder_level} ORDER BY e.datestart DESC)")
        cur = db.session.execute(cursorQuery)
        records = cur.fetchall()
        insertObject = []
        column_names = ['Название', 'Дата начала', 'Начало регистрации',
                        'Фамилия', 'Имя', 'Ссылка', 'ИД', 'Статус']
        for record in records:
            insertObject.append(dict(zip(column_names, record)))
        return json.dumps(insertObject, indent=4, default=str)
    else:
        return redirect(url_for('usuarios.profile'))


@events.route('/calend')
def calend():
    me = Users.query.filter_by(id=current_user.id).first_or_404()
    data = []
    category = ''
    for p in Events.query.all():
        if p.status == 1:
            if p.sfera == 'Научная':
                category = '#101257'
            elif p.sfera == 'Творческая':
                category = '#B01E15'
            elif p.sfera == 'Общественная':
                category = '#7820F8'
            elif p.sfera == 'Спортивная':
                category = '#FA611B'
            data.append({
                'title': p.name,
                'start_date': p.datestart,
                'end_date': p.dateend,
                'url': 'https://vkapi.me/e_' + p.link,
                'color': category
            })
    return render_template('calend.html', me=me, events=data)


@events.route('/get_calend')
def get_calend():
    data = []
    for p in Events.query.all():
        if p.status == 1:
            data.append({
                'title': p.name,
                'start_date': p.datestart,
                'end_date': p.dateend,
                'url': 'https://vkapi.me/event/' + p.link
            })
    resp = jsonify(data)
    return resp
