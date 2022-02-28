import os
class Config():
    #SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = '1911'
    # SQLALCHEMY_DATABASE_URI = ("postgresql://"+ os.environ['DB_USER'] + ":" 
    #                                      + os.environ['DB_PASSWORD']+ "@" 
    #                                      + os.environ['DB_HOST'] 
    #                                      + ":5432/dbdimasyour")
    SQLALCHEMY_DATABASE_URI = "postgresql://dimasyour:2010Dima@ls-1df9aef13459a18113cb0653831ba1e0acc7bf34.cfjjo2nbfwt5.eu-north-1.rds.amazonaws.com:5432/dbdimasyour"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'dimasyour@gmail.com'
    MAIL_PASSWORD = '0602DashaO'
    JSON_AS_ASCII = False