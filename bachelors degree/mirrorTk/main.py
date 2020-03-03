from io import StringIO
from tkinter import *
from news import *
import datetime as dt
from mirrorTk.news import *
from mirrorTk.UserProfiles import *

time_format = 12 # 12 or 24
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
            timeTick = self.timeObject.strftime('%I:%M %p') #hour in 12h format
        else:
            timeTick = self.timeObject.strftime('%H:%M') #hour in 24h format

        dayOfWeekTick = self.timeObject.strftime('%A')
        dateTick = self.timeObject.strftime(date_format)

        if timeTick != self.timeLabel.cget("text"):
            self.timeLabel.config(text=timeTick)

        if dayOfWeekTick != self.dayOfWeekLabel.cget("text"):
            self.dayOfWeekLabel.config(text=dayOfWeekTick)

        if dateTick != self.dateLabel.cget("text"):
            self.dateLabel.config(text=dateTick)


class Newsletter(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        self.configure(bg="black")
        self.newsHandler = News(parent.userHandler.activeUser['newsTopic'])
        self.newsLabel = Label(self, text="News :: Source " + self.newsHandler.keywords, font=("Helvetica", 20), fg="white", bg="black", justify="left")
        self.newsContainer = Frame(self, bg="black")
        self.newsContentLabel = Label(self.newsContainer, font=("Helvetica", 10), fg="white", bg="black", justify="left")

        self.newsContentLabel.pack(side="bottom", anchor="n")
        self.newsLabel.grid(row=0, column=0)
        self.newsContainer.grid(row=1, column=0)

    def refresh_news(self):
        newsString = StringIO()

        self.newsContentLabel.config(text=newsString.getvalue())

        print(self.newsContentLabel.cget('text'))

        for newsTitle in self.newsHandler.get_news():
            newsString.write(('\n' + newsTitle))

        self.newsContentLabel.config(text=newsString.getvalue())
        print(self.newsContentLabel.cget('text'))
        newsString.close()


class Window(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("mirror")
        self.configure(background="black")
        self.attributes("-fullscreen", True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.userHandler = UserProfiles()
        self.currentActiveUser = self.userHandler.activeUser
        self.newsFrame = Newsletter(self)
        self.clockFrame = Clock(self)

        self.clockFrame.place(x=self.winfo_screenwidth()*0.85, y=self.winfo_screenheight()*0.01)
        self.newsFrame.place(x=self.winfo_screenwidth()*0.01, y=self.winfo_screenheight()*0.02)
        self.update_tk()

    def update_tk(self):
        self.clockFrame.tick()
        self.userHandler.refresh_users_database()
        self.currentActiveUser = self.userHandler.activeUser

        if self.currentActiveUser != self.userHandler.activeUser:
            self.currentActiveUser = self.userHandler.activeUser

            self.newsFrame.newsHandler = News(self.currentActiveUser['newsTopic'])

        self.newsFrame.refresh_news()
        self.after(1000, self.update_tk)


if __name__ == "__main__":
    window = Window()

    window.mainloop()
