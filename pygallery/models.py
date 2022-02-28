from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from pygallery import db, login_manager
from flask_login import UserMixin
from flask import current_app
from sqlalchemy.sql.expression import func
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

@login_manager.user_loader
def load_user(usuario_id):
    return Usuario.query.get(int(usuario_id))

class Serializer(object):
    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}
    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

class Users(db.Model, UserMixin, Serializer):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120),  nullable=False)
    firstname = db.Column(db.String(120),  nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    uzname = db.Column(db.String(120), nullable=False)
    level = db.Column(db.Integer,  nullable=False)
    password = db.Column(db.String(250), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(120), nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return (f"Users('{self.firstname}', '{self.username}', '{self.lastname}', '{self.email}' , '{self.uzname}' , '{self.level}' ,'{self.password}', '{self.department}', '{self.avatar}')")
    
    def serialize(self):
        d = Serializer.serialize(self)
        del d['password']
        return d

class Events(db.Model, UserMixin):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sfera = db.Column(db.String(50), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    datestart = db.Column(db.DateTime, nullable=False)
    dateend = db.Column(db.DateTime, nullable=False)
    dateregstart = db.Column(db.DateTime, nullable=False)
    dateregend = db.Column(db.String(120), nullable=False)
    own = db.Column(db.Integer, nullable=False)
    moderator = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    link = db.Column(db.String(50), nullable=False, unique=True)
    dop = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return (f"Events('{self.name}', '{self.sfera}', '{self.level}', '{self.seats}', '{self.datestart}', '{self.dateend}', '{self.dateregstart}', '{self.dateregend}', '{self.own}', '{self.moderator}', '{self.status}', '{self.link}', '{self.dop}')")

class Eventship(db.Model, UserMixin):
    __tablename__ = 'eventship'
    eventshipid = db.Column(db.Integer, primary_key=True)
    eventlink = db.Column(db.Integer, db.ForeignKey(Events.link), nullable=False)
    memberid = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    memberrole = db.Column(db.Integer, nullable=False)
    nagrada = db.Column(db.Integer, nullable=False)

    event = relationship('Events', foreign_keys='Eventship.eventlink')
    member = relationship('Users', foreign_keys='Eventship.memberid')

    def __repr__(self):
        return (f"Eventship('{self.eventlink}', '{self.memberid}', '{self.memberrole}')")


class Event(db.Model, UserMixin):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return (f"Events('{self.id}', '{self.title}', '{self.url}', '{self.category}', '{self.start_date}', '{self.end_date}')")

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    imagen_perfil = db.Column(
        db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    imagenes = db.relationship('Imagen', backref="autor", lazy=True)
    repositorios = db.relationship(
        'Repositorio', backref="propietario", lazy=True)

    def __repr__(self):
        return f"Usuario('{self.username}','{self.email}','{self.imagen_perfil}')"

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return none
        return Usuario.query.get(user_id)



etiquetas = db.Table('etiquetas',
                     db.Column('etiqueta_id', db.Integer, db.ForeignKey(
                         'etiqueta.id'), primary_key=True),
                     db.Column('imagen_id', db.Integer, db.ForeignKey(
                         'imagen.id'), primary_key=True)
                     )


class Imagen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ubicacion_imagen = db.Column(db.String(20), nullable=False, unique=True)
    fecha_publicacion = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    etiquetas = db.relationship('Etiqueta', secondary=etiquetas,
                                lazy='subquery', backref=db.backref('imagenes', lazy=True))
    id_usuario = db.Column(db.Integer, db.ForeignKey(
        'usuario.id'), nullable=False)

    def __repr__(self):
        return f"Imagen('{self.ubicacion_imagen}','{self.fecha_publicacion}')"


class Etiqueta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"Etiqueta('{self.nombre}')"


imagenes_repositorio = db.Table('imagenes_repositorio',
                                db.Column('repositorio_id', db.Integer, db.ForeignKey(
                                    'repositorio.id'), primary_key=True),
                                db.Column('imagen_id', db.Integer, db.ForeignKey(
                                    'imagen.id'), primary_key=True)
                                )


class Repositorio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_repositorio = db.Column(db.String(20), nullable=False)
    id_propietario = db.Column(
        db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    descripcion = db.Column(db.String(100), nullable=True)
    imagenes = db.relationship('Imagen', secondary=imagenes_repositorio,
                               lazy='subquery', backref=db.backref('repositorios', lazy=True))

    def __repr__(self):
        return f"Repositorio('{self.nombre_repositorio}')"
