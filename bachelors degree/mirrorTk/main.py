import datetime as dt
from io import StringIO
from tkinter import *
import pickle
from googleapiclient.discovery import build

from mirrorTk.news import News
from mirrorTk.userProfiles import userProfiles

time_format = 12  # 12 or 24
date_format = "%b %d, %Y"


class Clock(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, bg='black')
        self.timeObject = dt.datetime.now()
        self.timeLabel = Label(self, font=('Helvetica', 45), fg="white", bg="black")
        self.dayOfWeekLabel = Label(self, font=('Helvetica', 20), fg="white", bg="black")
        self.dateLabel = Label(self, font=('Helvetica', 20), fg="white", bg="black")

        self.timeLabel.pack(side=TOP, anchor=E)
        self.dayOfWeekLabel.pack(side=TOP, anchor=E)
        self.dateLabel.pack(side=TOP, anchor=E)
        self.tick()

    def tick(self):
        self.timeObject = dt.datetime.now()

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
        self.calendarLbl = Label(self, text=self.title, font=('Helvetica', 28), fg="white", bg="black")
        self.calendarLbl.pack(side=TOP, anchor=E)
        self.calendarEventContainer = Frame(self, bg='black')
        self.calendarEventContainer.pack(side=TOP, anchor=E)
        self.parent = parent
        self.get_events()

    def get_events(self):
        with open('../' + self.parent.currentActiveUser['googleToken'], 'rb') as token:
            credentials = pickle.load(token)

        service = build('calendar', 'v3', credentials=credentials)

        events_result = service.events().list(calendarId='primary', timeMin=dt.datetime.utcnow().isoformat() + 'Z', \
                                              maxResults=5, singleEvents=True, orderBy='startTime').execute()

        events = events_result.get('items', [])

        for widget in self.calendarEventContainer.winfo_children():
            widget.destroy()

        for event in events:
            calendar_event = CalendarEvent(self.calendarEventContainer, event_name=event['summary'])
            calendar_event.pack(side=TOP, anchor=E)


class CalendarEvent(Frame):
    def __init__(self, parent, event_name="Event 1"):
        Frame.__init__(self, parent, bg='black')
        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('Helvetica', 18), fg="white", bg="black")
        self.eventNameLbl.pack(side=TOP, anchor=E)


class Newsletter(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        self.configure(bg="black")
        self.newsHandler = News(parent.currentActiveUser['newsTopic'])
        self.labelContainer = Frame(self, bg="black")
        self.label = Label(self.labelContainer, text="News", font=("Helvetica", 20), fg="white", bg="black",
                           justify="left")
        self.newsContainer = Frame(self, bg="black")
        self.newsContentLabel = Label(self.newsContainer, font=("Helvetica", 15), fg="white", bg="black",
                                      justify="left")

        self.label.pack(side="bottom", anchor="n")
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


class Window(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("mirror")
        self.configure(background="black")
        self.attributes("-fullscreen", True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.calendar_refresh_rate = 1800

        self.userHandler = userProfiles()
        self.currentActiveUser = self.userHandler.get_active_user()
        self.newsFrame = Newsletter(self)
        self.clockFrame = Clock(self)
        self.calendarFrame = Calendar(self)

        self.clockFrame.place(x=self.winfo_screenwidth() * 0.85, y=self.winfo_screenheight() * 0.01)
        self.newsFrame.place(x=self.winfo_screenwidth() * 0.01, y=self.winfo_screenheight() * 0.02)
        self.calendarFrame.place(x=self.winfo_screenwidth() * 0.85, y=self.winfo_screenheight() * 0.65)
        self.update_tk()

    def update_tk(self):
        self.clockFrame.tick()

        self.currentActiveUser = self.userHandler.get_active_user()

        self.calendar_refresh_rate -= 1
        if self.calendar_refresh_rate == 0:
            self.calendarFrame.get_events()
            self.calendar_refresh_rate = 1800

        self.newsFrame.newsHandler.replace_keyword(self.currentActiveUser['newsTopic'])
        self.newsFrame.refresh_news()
        self.after(1000, self.update_tk)


if __name__ == "__main__":
    window = Window()

    window.mainloop()
