import os


def get_project_path():
    return os.path.normpath(os.getcwd() + os.sep + os.pardir)


def get_number_of_pics():
    answer = []

    for name in os.listdir(get_project_path() + '/config/userPictures'):
        if os.path.isfile(get_project_path() + '/config/userPictures/' + name):
            answer.append(name)

    return len(answer)


class Config(object):
    SECRET_KEY = '0123456789'
    PROJECT_PATH = get_project_path()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + PROJECT_PATH + '/config/mirrorDatabase.db'
    # os.environ.get('DATABASE_URL') or \
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIRECT_URI = 'http://raspberry.tplinkdns.com:276/google'
    GOOGLE_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/gmail.readonly']
    PICTURE_FOLDER = PROJECT_PATH + '/config/userPictures'
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
    PICTURE_ID_FILENAME = get_number_of_pics() - 1  # .DS_Store reasons !!!!
    NEWS_WEBSITES = {
        "Sport Intern": "https://www.agerpres.ro/sport-intern",
        "Politica": "https://www.agerpres.ro/politica",
        "Sanatate": "https://www.agerpres.ro/sanatate",
        "Administratie": "https://www.agerpres.ro/administratie",
        "Cultura": "https://www.agerpres.ro/cultura",
        "Economic Extern": "https://www.agerpres.ro/economic-extern",
        "Declaratia zilei": "https://www.agerpres.ro/declaratia-zilei",
        "Mediu": "https://www.agerpres.ro/mediu",
        "Life": "https://www.agerpres.ro/life",
        "Eveniment": "https://www.agerpres.ro/eveniment",
        "Romania in lume": "https://www.agerpres.ro/romania-in-lume",
        "Viata Parlamentara": "https://www.agerpres.ro/viata-parlamentara",
        "Mondorama": "https://www.agerpres.ro/mondorama",
        "Revista presei": "https://www.agerpres.ro/revista-presei",
        "Reportaj": "https://www.agerpres.ro/reportaj",
        "Politica Externa": "https://www.agerpres.ro/politica-externa",
        "Romania Colorata": "https://www.agerpres.ro/romania-colorata",
        "Interviu": "https://www.agerpres.ro/interviu",
        "Documentare": "https://www.agerpres.ro/documentare",
        "Stirile zilei": "https://www.agerpres.ro/stirile-zilei",
        "Regionale": "https://www.agerpres.ro/regionale",
        "CyberSecurity": "https://www.agerpres.ro/cybersecurity",
        "Sport Extern": "https://www.agerpres.ro/sport-extern",
        "Justitie": "https://www.agerpres.ro/justitie",
        "Unic in Europa": "https://www.agerpres.ro/unic-in-europa",
        "Culte": "https://www.agerpres.ro/culte",
        "Social": "https://www.agerpres.ro/social",
        "Zig Zag": "https://www.agerpres.ro/zig-zag",
        "Stiinta&Tehnica": "https://www.agerpres.ro/stiintatehnica",
        "Planeta": "https://www.agerpres.ro/planeta",
        "Educatie-Stiinta": "https://www.agerpres.ro/educatie-stiinta",
        "Geopolitical Futures": "https://www.agerpres.ro/geopolitical-futures",
        "OTS": "https://www.agerpres.ro/ots",
        "Economic Intern": "https://www.agerpres.ro/economic-intern"
    }
