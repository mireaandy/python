from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from string import digits
import os
from cv2 import imread, cvtColor, COLOR_BGR2RGB, VideoCapture
import face_recognition
import pickle
import time


def get_project_path():
    return os.path.normpath(os.getcwd() + os.sep + os.pardir)


class Database:
    databaseEngine = create_engine('sqlite:///' + get_project_path() + '/config/mirrorDatabase.db')
    Model = declarative_base()

    Model.metadata.create_all(databaseEngine)

    session = sessionmaker(bind=databaseEngine)()

    @staticmethod
    def get_active_user(self):
        return Database.session.query(User).filter_by(isActive='1').first()

    @staticmethod
    def set_active_user(self, user_active):
        Database.get_active_user(None).isActive = 0
        Database.session.query(User).filter_by(username=user_active).first().isActive = 1
        Database.session.commit()


class User(Database.Model):

    __tablename__ = 'userData'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), index=False, unique=True, nullable=False)
    password = Column(String(128), index=False, unique=False, nullable=False)
    newsTopic = Column(String(50), index=False, unique=False, nullable=True)
    isActive = Column(String(1), index=False, unique=False, nullable=False)
    googleToken = Column(String(1000), index=False, unique=True, nullable=True)
    pictures = relationship('UserPicture', backref='user', lazy='dynamic')


class UserPicture(Database.Model):

    __tablename__ = 'userPictures'
    userId = Column(Integer, ForeignKey('userData.id'))
    pictureId = Column(Integer, primary_key=True)
    picturePath = Column(String(100), index=False, unique=True, nullable=False)
    encoded = Column(Integer, index=False, unique=False, nullable=False)


def encode_pictures():
    pictures = Database.session.query(UserPicture).filter_by(encoded=0).all()
    knownEncodings = []
    knownNames = []

    for pic in pictures:
        name = pic.picturePath.split('/')[-1].split('.')[0].translate(str.maketrans('', '', digits))
        image = imread(pic.picturePath)

        rgb = cvtColor(image, COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model='hog')
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

        pic.encoded = 1

        Database.session.commit()

    if len(pictures) != 0:
        data_all = {"encodings": knownEncodings, "names": knownNames}
        dump_file = open(get_project_path() + '/config/encodings.pickle', mode="rb")
        dump_file_size = os.path.getsize(dump_file.name)

        if dump_file_size != 0:
            data_old = pickle.load(dump_file)
            data_all.update(data_old)

        dump_file = open(get_project_path() + '/config/encodings.pickle', mode="wb")

        pickle.dump(obj=data_all, file=dump_file)
        dump_file.close()


def recognize_face():
    dump_file = open(get_project_path() + '/config/encodings.pickle', "rb")

    if os.path.getsize(dump_file.name) != 0:
        data = pickle.load(file=dump_file)
    else:
        data = None

    dump_file.close()

    if data is not None:
        camera = VideoCapture(index=0)
        time.sleep(0.1)
        if camera.isOpened():
            ret_val, frame = camera.read()
            camera.release()
            rgb = cvtColor(frame, COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model='hog')
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Default"

                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    name = max(counts, key=counts.get)
                names.append(name)

            if len(encodings) == 0:
                names.append("Default")

            print(names[0])
            Database.set_active_user(None, user_active=names[0])
