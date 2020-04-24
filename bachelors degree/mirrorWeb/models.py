from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app import database


class User(UserMixin, database.Model):
    __tablename__ = 'userData'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(100), index=False, unique=True, nullable=False)
    password = database.Column(database.String(128), index=False, unique=False, nullable=False)
    newsTopic = database.Column(database.String(50), index=False, unique=False, nullable=True)
    isActive = database.Column(database.String(1), index=False, unique=False, nullable=False)
    googleToken = database.Column(database.String(1000), index=False, unique=True, nullable=True)
    pictures = database.relationship('UserPicture', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class UserPicture(database.Model):
    __tablename__ = 'userPictures'
    userId = database.Column(database.Integer, database.ForeignKey('userData.id'))
    pictureId = database.Column(database.Integer, primary_key=True)
    picturePath = database.Column(database.String(100), index=False, unique=True, nullable=False)
    encoded = database.Column(database.Integer, index=False, unique=False, nullable=False)