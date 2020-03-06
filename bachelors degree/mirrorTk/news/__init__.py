import requests
from bs4 import BeautifulSoup

websites = {
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


class News:

    def __init__(self, keyword):
        self.keyword = keyword

    def replace_keyword(self, keyword):
        self.keyword = keyword

    def get_news(self):
        answer = []

        try:
            content = requests.get(websites[self.keyword]).content
        except:
            return answer

        soup = BeautifulSoup(content, "html5lib")
        news = soup.findAll("article", class_="unit_news shadow p_r")

        for newsPiece in news:
            titles = newsPiece.findAll("div", class_="title_news")

            for title in titles:
                answer.append(title.get_text())

        return answer
