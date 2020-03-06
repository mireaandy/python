from sqlite3 import *


class userProfiles:
    def __init__(self):
        self.activeUser = {}
        self.connectionDatabase = connect("../mirrorDatabase.db")
        self.usersDatabase = [{}]
        self.getUsersCommand = 'SELECT {} FROM userData;'
        self.populate_users_database()

    def get_active_user(self):
        self.refresh_users_database()
        return self.activeUser

    def update_active_user(self):
        found = False

        if len(self.usersDatabase) < 1:
            pass

        for index in range(len(self.usersDatabase)):
            if self.usersDatabase[index].get('isActive') == '1':
                found = True
                self.activeUser = self.usersDatabase[index]
                break

        if not found:
            self.activeUser = self.usersDatabase[1]

    def populate_users_database(self):
        cursor = self.connectionDatabase.cursor()

        cursor.execute(self.getUsersCommand.format('*'))

        data = cursor.fetchall()

        for row in data:
            self.usersDatabase.append({'userName': row[1], 'newsTopic': row[2], 'isActive': row[3]})

        cursor.close()
        self.update_active_user()

    def refresh_users_database(self):
        self.usersDatabase = [{}]

        self.populate_users_database()
