from datetime import datetime, timedelta
import json
from io import StringIO
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
            timeTick = self.timeObject.strftime('%I:%M %p')  # hour in 12h format
        else:
            timeTick = self.timeObject.strftime('%H:%M')  # hour in 24h format

        dayOfWeekTick = self.timeObject.strftime('%A')
        dateTick = self.timeObject.strftime(date_format)

        if timeTick != self.timeLabel.cget("text"):
            self.timeLabel.config(text=timeTick)

        if dayOfWeekTick != self.dayOfWeekLabel.cget("text"):
            self.dayOfWeekLabel.config(text=dayOfWeekTick)

        if dateTick != self.dateLabel.cget("text"):
            self.dateLabel.config(text=dateTick)


class Calendar(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.title = 'Calendar Events'
        self.calendarLabel = Label(self, text=self.title, font=('Helvetica', 28), fg="white", bg="black")
        self.calendarEventContainer = Frame(self, bg='black')
        self.parent = parent

        self.calendarLabel.pack(side=TOP, anchor=W)
        self.calendarEventContainer.pack(side=TOP, anchor=E)

    def get_events(self):
        for widget in self.calendarEventContainer.winfo_children():
            widget.destroy()

        if self.parent.currentActiveUser.username != 'Default':
            with open(self.parent.currentActiveUser.googleToken, 'rb') as token:
                credentials = pickle.load(token)

            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())

            service = build('calendar', 'v3', credentials=credentials)

            events_result = service.events().list(calendarId='primary', timeMin=datetime.utcnow().isoformat() + 'Z',
                                                  timeMax=(datetime.utcnow() + timedelta(hours=24)).isoformat() + 'Z',
                                                  maxResults=5, singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])

            for widget in self.calendarEventContainer.winfo_children():
                widget.destroy()

            for event in events:
                event_text = event['start']['dateTime'].split('T')[0] + ' ' + \
                             event['start']['dateTime'].split('T')[1].split('+')[0] + ' ' + event['summary']
                calendar_event = CalendarEvent(self.calendarEventContainer, event_name=event_text)
                calendar_event.pack(side=TOP, anchor=E)
        else:
            for widget in self.calendarEventContainer.winfo_children():
                widget.destroy()


class CalendarEvent(Frame):
    def __init__(self, parent, event_name="Event 1"):
        Frame.__init__(self, parent, bg='black')
        self.eventName = event_name
        self.eventNameLabel = Label(self, text=self.eventName, font=('Helvetica', 18), fg="white", bg="black")
        self.eventNameLabel.pack(side=TOP, anchor=E)


class Newsletter(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.configure(bg="black")
        self.newsHandler = News(parent.currentActiveUser.newsTopic)
        self.labelContainer = Frame(self, bg="black")
        self.label = Label(self.labelContainer, text="News", font=("Helvetica", 28), fg="white", bg="black",
                           justify="left")
        self.newsContainer = Frame(self, bg="black")
        self.newsContentLabel = Label(self.newsContainer, font=("Helvetica", 15), fg="white", bg="black",
                                      justify="left")

        self.label.pack(side="bottom", anchor=W)
        self.newsContentLabel.pack()
        self.labelContainer.grid(row=0, column=0)
        self.newsContainer.grid(row=1, column=0)

    def refresh_news(self):
        newsString = StringIO()

        self.newsContentLabel.config(text=newsString.getvalue())

        for newsTitle in self.newsHandler.get_news():
            newsString.write(('\n' + newsTitle))

        self.newsContentLabel.config(text=newsString.getvalue())
        newsString.close()


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
            self.iconLabell.config(image='')

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
        self.three_min_refresh_rate = 0
        self.database = Database()
        self.currentActiveUser = Database.get_active_user(None)
        self.newsFrame = Newsletter(self)
        self.clockFrame = Clock(self)
        self.calendarFrame = Calendar(self)
        self.weatherFrame = Weather(self)

        self.clockFrame.place(x=self.winfo_screenwidth() * 0.85, y=self.winfo_screenheight() * 0.01)
        self.newsFrame.place(x=self.winfo_screenwidth() * 0.01, y=self.winfo_screenheight() * 0.02)
        self.calendarFrame.place(x=self.winfo_screenwidth() * 0.01, y=self.winfo_screenheight() * 0.75)
        self.weatherFrame.place(x=self.winfo_screenwidth() * 0.77, y=self.winfo_screenheight() * 0.75)
        self.update_tk()

    def update_tk(self):
        self.clockFrame.tick()

        self.currentActiveUser = Database.get_active_user(None)
        self.newsFrame.newsHandler.replace_keyword(self.currentActiveUser.newsTopic)

        if self.three_min_refresh_rate == 5:
            self.weatherFrame.get_weather()
            encode_pictures()
            recognize_face()
            self.calendarFrame.get_events()
            self.newsFrame.refresh_news()
            self.three_min_refresh_rate = 0

        self.three_min_refresh_rate += 1

        self.after(1000, self.update_tk)


if __name__ == '__main__':
    window = Window()
    window.mainloop()
