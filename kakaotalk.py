# data file encoded in UTF-8

log_mode = False

def log(message):
    if log_mode:
        print(message)

# using regex module
import re
from datetime import datetime, date, time

class Chat:

    time = None # datetime object
    name = None
    message = None

    def __init__(self, data, date):
        matches = re.match(r'\[(.{,20})\] \[(.{,8})\] (.*)', data)

        if matches is not None:
            if date is not None:
                self.time = datetime.combine(date, datetime.strptime(matches.group(2), "%I:%M %p").time())
            self.name = matches.group(1)
            self.message = matches.group(3)

    def append(self, data):
        self.message = self.message + '\n' + data

    def get_words(self):
        if self.message is not None:
            return self.message.split(' ')
        else:
            return []

    def get_word_count(self):
        return len(self.get_words())

    def get_character_count(self):
        count = 0

        for word in self.get_words():
            count += len(word)

        return count

class Invite:

    host = None
    guest = None

    def __init__(self, data):
        matches = re.match(r'(.*) invited (.*)\.', data)
        host = matches.group(1)
        guest = matches.group(2)

class Leave:

    name = None

    def __init__(self, data):
        matches = re.match(r'(.*) left\.', data)
        name = matches.group(1)

class Chatroom:

    name = None
    date_saved = None
    chats = [] # chat object list
    invites = []
    leaves = []
    start_date = None
    end_date = None

    def __init__(self, filename):
        # split date / chats
        log("Slicing text data")
        regex = '|'.join([
                 '(\\[.{,20}\\] \\[.{,8}\\] .*)',               # chat
                 '--------------- (.+) ---------------', # date
                 '(.* invited .*\\.)',                   # invite
                 '(.* left\\.)'                          # leave
                 ])

        date = None

        f = open(filename, 'r', encoding='UTF-8')
        
        for line in f:

            matches = re.match(regex, line)
            
            if matches is not None and matches.group(1) is not None:
                self.chats.append(Chat(line, date))
                log("Added chat with date " + str(date))
                continue
                
            if matches is not None and matches.group(2) is not None:
                date = datetime.strptime(re.match(regex, line).group(2), "%A, %B %d, %Y")
                if self.start_date is -1:
                    self.start_date = self.date
                log("Added date: " + str(date))
                continue

            if matches is not None and matches.group(3) is not None:
                self.invites.append(Invite(line))
                log("Added invite")
                continue

            if matches is not None and matches.group(4) is not None:
                self.leaves.append(Leave(line))
                log("Added left")
                continue

            if len(self.chats) is 0:
                # metadata
                matches = re.match(r'(.*) with|Date Saved : (.*)', line)
                
                if matches is not None and matches.group(1) is not None:
                    name = re.match(r'(.*) with|Date Saved : (.*)', line).group(1)
                    log("Chatroom name: " + name)
                    continue
                    
                if matches is not None and matches.group(2) is not None:
                    self.date_saved = datetime.strptime(re.match(r'(.*) with|Date Saved : (.*)', line).group(2), "%Y-%m-%d %H:%M:%S")
                    log("Date saved: " + str(self.date_saved))
                    continue
                
            elif self.chats[-1] is Chat:
                # multi-line message
                self.chats[-1].append(line)
                log("Added multi-line chat")

        f.close()

        self.end_date = date

    def get_chat_span(self):
        return (self.start_date, self.end_date)

    def get_chat_span_days(self):
        return (self.end_date - self.start_date).days

    def get_total_chats(self):
        return len(self.chats)

    def get_total_words(self):
        count = 0
        
        for chat in self.chats:
            count += chat.get_word_count()

        return count

    def get_total_characters(self):
        count = 0

        for chat in self.chats:
            count += chat.get_character_count()

        return count

    def get_daily_chats(self):
        result = []
        count = 0

        for i in range(len(self.chats)):
            count += 1
            try:
                if self.chats[i].time.date != self.chats[i + 1].time.date:
                    # day change
                    result.append((self.chats[i].time.date, count))
            except:
                result.append((self.chats[i].time.date, count))

        return result

    def get_daily_words(self):
        result = []
        count = 0
        
        for i in range(len(self.chats)):
            count += self.chats[i].get_word_count()
            
            try:
                if self.chats[i].time.date != self.chats[i + 1].time.date:
                    # day change
                    result.append((self.chats[i].time.date, count))
            except:
                result.append((self.chats[i].time.date, count))

        return result

    def get_daily_characters(self):
        result = []
        count = 0
        
        for i in range(len(self.chats)):
            count += self.chats[i].get_character_count()
            
            try:
                if self.chats[i].time.date != self.chats[i + 1].time.date:
                    # day change
                    result.append((self.chats[i].time.date, count))
            except:
                result.append((self.chats[i].time.date, count))

        return result

    def get_hourly_chats(self):
        result = [0] * 24

        for chat in self.chats:
            hour = chat.time.hour
            result[hour] += 1

        return result

    def get_hourly_words(self):
        result = [0] * 24

        for chat in self.chats:
            hour = chat.time.hour
            result[hour] += chat.get_word_count()

        return result

    def get_hourly_characters(self):
        result = [0] * 24

        for chat in self.chats:
            hour = chat.time.hour
            result[hour] += chat.get_character_count()

        return result

    def get_weekly_chats(self):
        result = [0] * 7

        for chat in self.chats:
            day = chat.time.weekday()
            result[day] += 1

        return result

test_filename = "data.txt"

chat = Chatroom(test_filename)
print(chat.get_total_chats())
print(chat.get_total_words())
print(chat.get_total_characters())

hourly = chat.get_hourly_words()

for i in range(24):
    print("%2d:00, %4d words" % (i, hourly[i]))
