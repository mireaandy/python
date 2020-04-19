import os


class Config(object):
    SECRET_KEY = '0123456789'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////Users/andreimirea/Documents/GitHub/python/bachelors degree/mirrorDatabase.db'
    # os.environ.get('DATABASE_URL') or \
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
