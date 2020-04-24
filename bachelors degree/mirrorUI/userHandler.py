from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from string import digits
import os
import cv2
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

    def get_active_user(self):
        return self.session.query(User).filter_by(isActive='1').first()


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
        image = cv2.imread(pic.picturePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model='hog')
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            knownEncodings.append(encoding)
            knownNames.append(name)

        pic.encoded = 1

        Database.session.commit()

    if len(pictures) != 0:
        data = {"encodings": knownEncodings, "names": knownNames}
        dump_file = open(get_project_path() + '/config/encodings.pickle', mode="wb")

        pickle.dump(obj=data, file=dump_file)
        dump_file.close()


def recognize_face():
    dump_file = open(get_project_path() + '/config/encodings.pickle', "rb")
    data = pickle.load(file=dump_file)
    dump_file.close()

    detector = cv2.CascadeClassifier(get_project_path() + '/config/haarcascade_frontalface_default.xml')
    camera = cv2.VideoCapture(0)
    time.sleep(0.1)
    if camera.isOpened():
        ret_val, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"

            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)
            names.append(name)
            print(names)

        camera.release()
