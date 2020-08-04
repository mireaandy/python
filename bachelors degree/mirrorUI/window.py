from datetime import datetime
import json
from tkinter import *
import pickle
import requests
from PIL import Image, ImageTk
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from news import News
from userHandler import Database, encode_pictures, recognize_face, get_project_path

time_format = 12
date_format = "%b %d, %Y"

WEATHER_ICONS = {
    'clear-day': f"{get_project_path()}/config/weatherIcons/Sun.png",
    'wind': f"{get_project_path()}/config/weatherIcons/Wind.png",
    'cloudy': f"{get_project_path()}/config/weatherIcons/Cloud.png",
    'partly-cloudy-day': f"{get_project_path()}/config/weatherIcons/PartlySunny.png",
    'rain': f"{get_project_path()}/config/weatherIcons/Rain.png",
    'snow': f"{get_project_path()}/config/weatherIcons/Snow.png",
    'snow-thin': f"{get_project_path()}/config/weatherIcons/Snow.png",
    'fog': f"{get_project_path()}/config/weatherIcons/Haze.png",
    'clear-night': f"{get_project_path()}/config/weatherIcons/Moon.png",
    'partly-cloudy-night': f"{get_project_path()}/config/weatherIcons/PartlyMoon.png",
    'thunderstorm': f"{get_project_path()}/config/weatherIcons/Storm.png",
    'tornado': f"{get_project_path()}/config/weatherIcons/Tornado.png",
    'hail': f"{get_project_path()}/config/weatherIcons/Hail.png"
}


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.timeObject = datetime.now()
        self.timeLabel = Label(self, font=('Helvetica', 45), fg="white", bg="black")
        self.dayOfWeekLabel = Label(self, font=('Helvetica', 20), fg="white", bg="black")
        self.dateLabel = Label(self, font=('Helvetica', 20), fg="white", bg="black")

        self.timeLabel.pack(side=TOP, anchor=E)
        self.dayOfWeekLabel.pack(side=TOP, anchor=E)
        self.dateLabel.pack(side=TOP, anchor=E)
        self.tick()

    def tick(self):
        self.timeObject = datetime.now()

        if time_format == 12:
            time_tick = self.timeObject.strftime('%I:%M %p')  # hour in 12h format
        else:
            time_tick = self.timeObject.strftime('%H:%M')  # hour in 24h format

        day_of_week_tick = self.timeObject.strftime('%A')
        date_tick = self.timeObject.strftime(date_format)

        if time_tick != self.timeLabel.cget("text"):
            self.timeLabel.config(text=time_tick)

        if day_of_week_tick != self.dayOfWeekLabel.cget("text"):
            self.dayOfWeekLabel.config(text=day_of_week_tick)

        if date_tick != self.dateLabel.cget("text"):
            self.dateLabel.config(text=date_tick)


class Email(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.title = 'Emails'
        self.noTitle = ''
        self.emailLabel = Label(self, text=self.title, font=('Helvetica', 28), fg="white", bg="black")
        self.emailSubjectContainer = Frame(self, bg='black')
        self.parent = parent

        self.emailLabel.pack(side=TOP, anchor=W)
        self.emailSubjectContainer.pack(side=TOP, anchor=E)

    def get_emails(self):
        for widget in self.emailSubjectContainer.winfo_children():
            widget.destroy()

        if self.parent.currentActiveUser.username != 'Default':
            self.emailLabel['text'] = self.title

            with open(self.parent.currentActiveUser.googleToken, 'rb') as token:
                credentials = pickle.load(token)

            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())

            service = build('gmail', 'v1', credentials=credentials)
            response = service.users().messages().list(userId='me', labelIds=['UNREAD']).execute()
            old_parent_property_value = self.parent.noEmailsDisplayed

            for message in response['messages']:
                self.parent.noEmailsDisplayed -= 1

                if self.parent.noEmailsDisplayed == -1:
                    self.parent.noEmailsDisplayed = old_parent_property_value
                    break

                display_response = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                email_headers = display_response['payload'].get('headers')
                label_body = next( item['value'].split('<')[0].split('>')[0] for item in email_headers
                                   if item["name"] == "From" ) + ' : ' + next( item['value'] for item in email_headers
                                                                             if item["name"] == "Subject" )
                email_element = EmailElement(self.emailSubjectContainer, email_subject=label_body)

                email_element.pack(side=TOP, anchor=W)
        else:
            self.emailLabel['text'] = self.noTitle


class EmailElement(Frame):
    def __init__(self, parent, email_subject='Email subject 1'):
        Frame.__init__(self, parent, bg='black')

        self.emailSubject = email_subject
        self.emailSubjectLabel = Label(self, text=self.emailSubject, font=('Helvetica', 14), fg="white", bg="black", wraplength=500)

        self.emailSubjectLabel.pack(side=TOP, anchor=W)


class Calendar(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.title = 'Calendar Events'
        self.noTitle = ''
        self.calendarLabel = Label(self, text=self.title, font=('Helvetica', 28), fg="white", bg="black")
        self.calendarEventContainer = Frame(self, bg='black')
        self.parent = parent

        self.calendarLabel.pack(side=TOP, anchor=W)
        self.calendarEventContainer.pack(side=TOP, anchor=E)

    def get_events(self):
        for widget in self.calendarEventContainer.winfo_children():
            widget.destroy()

        if self.parent.currentActiveUser.username != 'Default':
            self.calendarLabel['text'] = self.title

            with open(self.parent.currentActiveUser.googleToken, 'rb') as token:
                credentials = pickle.load(token)

            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())

            service = build('calendar', 'v3', credentials=credentials)
            events_result = service.events().list(calendarId='primary', timeMin=datetime.utcnow().isoformat() + 'Z',
                                                  maxResults=5, singleEvents=True).execute()
            events = events_result.get('items', [])

            for widget in self.calendarEventContainer.winfo_children():
                widget.destroy()

            for event in events:
                event_text = event['start']['dateTime'].split('T')[0] + ' ' + \
                             event['start']['dateTime'].split('T')[1].split('+')[0] + ' ' + event['summary']
                calendar_event = CalendarEvent(self.calendarEventContainer, event_name=event_text)
                calendar_event.pack(side=TOP, anchor=E)
        else:
            self.calendarLabel['text'] = self.noTitle


class CalendarEvent(Frame):
    def __init__(self, parent, event_name="Event 1"):
        Frame.__init__(self, parent, bg='black')

        self.eventName = event_name
        self.eventNameLabel = Label(self, text=self.eventName, font=('Helvetica', 18), fg="white", bg="black")

        self.eventNameLabel.pack(side=TOP, anchor=E)


class Newsletter(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.title = 'News'
        self.newsHandler = News(parent.currentActiveUser.newsTopic)
        self.newsLabel = Label(self, text=self.title, font=("Helvetica", 28), fg="white", bg="black", justify="left")
        self.newsElementContainer = Frame(self, bg="black")
        self.parent = parent

        self.newsLabel.pack(side=TOP, anchor=W)
        self.newsElementContainer.pack(side=TOP, anchor=E)

    def get_news(self):
        for widget in self.newsElementContainer.winfo_children():
            widget.destroy()

        for newsTitle in self.newsHandler.get_news():
            news_element = NewsElement(self.newsElementContainer, news_title=newsTitle)
            news_element.pack(side=TOP, anchor=W)


class NewsElement(Frame):
    def __init__(self, parent, news_title="News 1"):
        Frame.__init__(self, parent, bg='black')
        self.newsTitle = news_title
        self.newsTitleLabel = Label(self, text=self.newsTitle, font=('Helvetica', 14), fg="white", bg="black")
        self.newsTitleLabel.pack(side=TOP, anchor=E)


class Weather(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.degreeFrame = Frame(self, bg="black")
        self.degreeFrame.pack(side=TOP, anchor=W)
        self.temperatureLabel = Label(self.degreeFrame, font=('Helvetica', 25), fg="white", bg="black")
        self.temperatureLabel.pack(side=LEFT, anchor=N)
        self.iconLabel = Label(self.degreeFrame, bg="black")
        self.iconLabel.pack(side=LEFT, anchor=N, padx=20)
        self.currentlyLabel = Label(self, font=('Helvetica', 20), fg="white", bg="black")
        self.currentlyLabel.pack(side=TOP, anchor=W)
        self.forecastLabel = Label(self, font=('Helvetica', 15), fg="white", bg="black")
        self.forecastLabel.pack(side=TOP, anchor=W)
        self.locationLabel = Label(self, font=('Helvetica', 15), fg="white", bg="black")
        self.locationLabel.pack(side=TOP, anchor=W)

    @staticmethod
    def get_ip():
        ip_url = "http://jsonip.com/"
        req = requests.get(ip_url)
        ip_json = json.loads(req.text)
        return ip_json['ip']

    def get_weather(self):
        location_req_url = f"http://api.ipstack.com/{self.get_ip()}?access_key=11442fd93a2b6f35695a8bda9f2891f9"

        response_ip = requests.get(location_req_url)
        location_obj = json.loads(response_ip.text)

        lat = location_obj['latitude']
        lon = location_obj['longitude']

        location2 = f"{location_obj['city']}, {location_obj['region_code']}"

        weather_req_url = f"https://api.darksky.net/forecast/8da1b82e7ba6ae18bdf188c489a852d6/{lat},{lon}?lang=ro&units=si"

        response_weather = requests.get(weather_req_url)
        weather_obj = json.loads(response_weather.text)

        degree_sign = u'\N{DEGREE SIGN}'
        temperature2 = "%s%s C" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
        currently2 = weather_obj['currently']['summary']
        forecast2 = weather_obj["hourly"]["summary"]

        icon_id = weather_obj['currently']['icon']
        icon2 = None

        if icon_id in WEATHER_ICONS:
            icon2 = WEATHER_ICONS[icon_id]

        if icon2 is not None:
            if self.icon != icon2:
                self.icon = icon2
                image = Image.open(icon2)
                image = image.resize((100, 100), Image.ANTIALIAS)
                image = image.convert('RGB')
                photo = ImageTk.PhotoImage(image)

                self.iconLabel.config(image=photo)
                self.iconLabel.image = photo
        else:
            self.iconLabel.config(image='')

        if self.currently != currently2:
            self.currently = currently2
            self.currentlyLabel.config(text=currently2)
        if self.forecast != forecast2:
            self.forecast = forecast2
            self.forecastLabel.config(text=forecast2)
        if self.temperature != temperature2:
            self.temperature = temperature2
            self.temperatureLabel.config(text=temperature2)
        if self.location != location2:
            if location2 == ", ":
                self.location = "Cannot Pinpoint Location"
                self.locationLabel.config(text="Cannot Pinpoint Location")
            else:
                self.location = location2
                self.locationLabel.config(text=location2)


class Window(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("mirror")
        self.configure(background="black")
        self.attributes("-fullscreen", True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.threeMinRefreshRate = 0
        self.database = Database()
        self.currentActiveUser = Database.get_active_user(None)
        self.newsFrame = Newsletter(self)
        self.clockFrame = Clock(self)
        self.calendarFrame = Calendar(self)
        self.weatherFrame = Weather(self)
        self.emailFrame = Email(self)
        self.noEmailsDisplayed = 5

        self.clockFrame.place(x=self.winfo_screenwidth() * 0.85, y=self.winfo_screenheight() * 0.01)
        self.newsFrame.place(x=self.winfo_screenwidth() * 0.01, y=self.winfo_screenheight() * 0.02)
        self.calendarFrame.place(x=self.winfo_screenwidth() * 0.01, y=self.winfo_screenheight() * 0.75)
        self.weatherFrame.place(x=self.winfo_screenwidth() * 0.85, y=self.winfo_screenheight() * 0.75)
        self.emailFrame.place(x=self.winfo_screenwidth()*0.40, y=self.winfo_screenheight()*0.75)
        self.update_tk()

    def update_tk(self):
        self.clockFrame.tick()

        self.currentActiveUser = Database.get_active_user(None)
        self.newsFrame.newsHandler.replace_keyword(self.currentActiveUser.newsTopic)

        if self.threeMinRefreshRate == 5:
            self.weatherFrame.get_weather()
            encode_pictures()
            recognize_face()
            self.calendarFrame.get_events()
            self.newsFrame.get_news()
            self.emailFrame.get_emails()
            self.threeMinRefreshRate = 0

        self.threeMinRefreshRate += 1

        self.after(1000, self.update_tk)


if __name__ == '__main__':
    window = Window()
    window.mainloop()
