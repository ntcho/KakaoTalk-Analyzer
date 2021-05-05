"""Provides a structure to store the statistics of the chat as an instance.

Stores the full statistics of the entire chatroom, or a simple metadata of a 
single chat. Includes an extensive set of getters for various types of
statistics.

  Typical usage example:

  foo = Chatroom()
  bar = foo.message_count
"""


from datetime import datetime


class Message:
    """A class used to represent a message in a chatroom.

    This class supports counting functions that can be used to create statistic
    values. Will be mostly used as a part of `kakaotalk.Chatroom` instance.

    Attributes:
        time: A datetime instance of the time which the message was sent.
        author: A string of the name of the participant who sent the message.
        content: A string of the content of the message.
        rich_content_type: A string indicating the type of rich content message.
        rich_content_duration: A integer representing duration in seconds for
                               applicable rich contents such as voice call, 
                               video call and Live Talk.
    """
    time = None
    author = None
    content = None
    rich_content_type = None
    rich_content_duration = None

    def __init__(self, time: datetime, author: str, content: str, 
                 rich_content_type: str = None, rich_content_duration = None) -> None:
        """Initializes Message with time, author, content, type of the rich 
           content and duration of the rich content.
        """
        self.time = time
        self.author = author
        self.content = content
        self.rich_content_type = rich_content_type
        self.rich_content_duration = rich_content_duration

    def append(self, content: str) -> None:
        """Appends extra content to the message.

        Used for multi-line messages containing new lines in the message.

        Args:
            content (str): A string of the content to append.
        """
        self.content = self.content + '\n' + content

    def get_hour(self) -> int:
        """Returns the hour of the time which the message was sent.

        Returns:
            int: An integer representation of the hour in 24H format.
                 For example, 12AM will be returned as 0.
        """
        return self.time.hour

    def get_words(self) -> list:
        """Returns the list of words in the message.

        Returns:
            list: A list of words included in the message.
        """
        return self.content.split(' ')

    def get_word_count(self) -> int:
        """Returns the number of words in the message.

        Returns:
            int: A number of words included in the message.
        """
        return len(self.get_words())

    def get_letter_count(self) -> int:
        """Returns the number of letters in the message.

        Total number of letters, excluding whitespaces. Computed with
        `(length of the content) - (number of whitespaces)`.

        Returns:
            int: A number of letters included in the message.
        """
        return len(self.content) - self.content.count(' ')


class Event:
    """A class used to represent an event that can happen in a KakaoTalk chatroom.

    Currently there are 2 types of events possible, participants being invited
    and leaving.

    Attributes:
        event_type: A string of the type of the event.
                    Will be either 'invite' or 'leave'.
        content: A string of the content of the event.
    """
    event_type = None
    content = None

    def __init__(self, event_type: str, content: str) -> None:
        """Initializes Event from event type and content.

        Args:
            event_type (str): A string of the type of the event.
            content (str): A string of the content of the event.
        """
        self.event_type = event_type
        self.content = content


class Chatroom:
    """A class used to represent a KakaoTalk chatroom.

    An object of this class will contain all the statistic information about
    the chatroom including number of messages, number of participants, and 
    many more.

    Attributes:
        title: A string of the title of the chatroom provided in the chat log.
        date_saved: A datetime instance of the date which the chat log was saved.
        messages: A list of `kakaotalk.Message` instances.
        events: A list of `kakaotalk.Event` instances.
        start_date: A datetime instance of the first message in the chatroom.
        end_date: A datetime instance of the last message in the chatroom.

    Notes:
        I've thought about whether to save everything as kakaotalk.Message
        instances and recomputing the values while iterating through the list
        again, or to compute it as the analyzer parses from the file. Since the
        chat log file tends to be quite big and there will be file I/O delays,
        I designed this component to compute the statistic values on-the-go.
        Please open an issue or PR if you have any idea for better performance.
    """

    title = None
    date_saved = None
    messages = []
    events = []
    start_date = None
    end_date = None

    # Local variables used for statistics

    message_count = 0
    message_count_by_month = {}  # {'yymm': int} format
    message_count_by_day_of_week = {}  # {int: int} format, key 0 being Monday
    message_count_by_time_of_day = {}  # {int: int} format, key 0 being 12AM
    message_count_by_participant = {}  # {'name': int} format
    message_count_by_participant_and_month = {}  # {'yymm': {'name': int}} format

    day_count = 0
    word_count = 0
    letter_count = 0

    date_most_active_message = (None, -1)  # (datetime, int) format
    date_most_active_media = (None, -1)  # (datetime, int) format
    date_most_active_sticker = (None, -1)  # (datetime, int) format

    date_message_count = 0
    date_media_count = 0
    date_sticker_count = 0

    rich_content_count = {
        'sticker': 0,
        'photo': 0,
        'video': 0,
        'deleted': 0,
        'voice_note': 0,
        'youtube_link': 0,
        'link': 0,
        'file': 0,
        'voice_call': 0,
        'video_call': 0,
        'live_talk': 0,
    }

    rich_content_duration = {
        'voice_call': 0,  # in seconds
        'video_call': 0,  # in seconds
        'live_talk': 0,  # in seconds
    }

    event_count = {
        'invite': 0,
        'leave': 0
    }

    def __init__(self, title: str, date_saved: datetime) -> None:
        """Initializes Chatroom from title and saved date.

        Args:
            title (str): A string of the title of the chatroom.
            date_saved (datetime): A datetime instance of the saved date metadata.
        """
        self.title = title
        self.date_saved = date_saved
    
    def add_message(self, msg: Message) -> None:
        """Adds a message to the Chatroom instance.

        Args:
            msg (Message): A kakaotalk.Message instance.
        """
        self.messages.append(msg)

        # Remove _hr exception
        if msg.rich_content_type is not None and '_hr' in msg.rich_content_type:
            # Remove '_hr' from the last message instance
            self.messages[-1].rich_content_type = msg.rich_content_type.replace('_hr', '')

        # message_count
        self.message_count += 1

        # message_count_by_month
        month = msg.time.strftime('%Y%m')
        if month in self.message_count_by_month:
            self.message_count_by_month[month] += 1
        else:
            self.message_count_by_month[month] = 1

        # message_count_by_day_of_week
        day = msg.time.weekday()
        if day in self.message_count_by_day_of_week:
            self.message_count_by_day_of_week[day] += 1
        else:
            self.message_count_by_day_of_week[day] = 1
        
        # message_count_by_time_of_day
        hour = msg.get_hour()
        if hour in self.message_count_by_time_of_day:
            self.message_count_by_time_of_day[hour] += 1
        else:
            self.message_count_by_time_of_day[hour] = 1

        # message_count_by_participant
        if msg.author in self.message_count_by_participant:
            self.message_count_by_participant[msg.author] += 1
        else:
            self.message_count_by_participant[msg.author] = 1

        # message_count_by_participant_and_month
        if month in self.message_count_by_participant_and_month:
            if msg.author in self.message_count_by_participant_and_month[month]:
                self.message_count_by_participant_and_month[month][msg.author] += 1
            else:
                self.message_count_by_participant_and_month[month][msg.author] = 1
        else:
            self.message_count_by_participant_and_month[month] = {msg.author: 1}

        
        # word_count
        self.word_count += msg.get_word_count()

        # letter_count
        self.letter_count += msg.get_letter_count()


        # date_message_count
        self.date_message_count += 1

        # date_media_count
        if msg.rich_content_type is 'photo' or msg.rich_content_type is 'video':
            self.date_media_count += 1
        
        # date_sticker_count
        if msg.rich_content_type is 'sticker':
            self.date_sticker_count += 1

        
        # rich_content_count
        if msg.rich_content_type is not None:
            self.rich_content_count[msg.rich_content_type] += 1
        
        # rich_content_duration
        if msg.rich_content_duration is not None:
            self.rich_content_duration[msg.rich_content_type] += \
                msg.rich_content_duration

    def add_event(self, event: Event) -> None:
        """Adds an event to the Chatroom instance.

        Args:
            event (Event): A kakaotalk.Event instance.
        """
        self.events.append(event)

        self.event_count[event.event_type] += 1

    def set_start_date(self, date: datetime) -> None:
        """Sets start date of the chatroom.

        Args:
            date (datetime): A datetime instance of the first message.
        """
        self.start_date = date

    def set_end_date(self, date: datetime) -> None:
        """Sets end date of the chatroom.

        Called by parser.py when it matches a date tag.

        Args:
            date (datetime): A datetime instance of the last message.
        """
        # Update most active day
        if self.date_most_active_message[1] < self.date_message_count:
            self.date_most_active_message = (self.end_date, self.date_message_count)
        if self.date_most_active_media[1] < self.date_media_count:
            self.date_most_active_media = (self.end_date, self.date_media_count)
        if self.date_most_active_sticker[1] < self.date_sticker_count:
            self.date_most_active_sticker = (self.end_date, self.date_sticker_count)

        self.end_date = date
        
        # Reset daily counter
        self.date_message_count = 0
        self.date_media_count = 0
        self.date_sticker_count = 0

        # day_count
        self.day_count += 1

    def get_average_words_per_message(self) -> float:
        return self.word_count / self.message_count
    
    def get_average_letters_per_message(self) -> float:
        return self.letter_count / self.message_count

    def get_average_messages_per_day(self) -> float:
        return self.message_count / self.day_count
    
    def get_average_letters_per_day(self) -> float:
        return self.letter_count / self.day_count
    
    def __str__(s) -> str:
        return f"""KakaoTalk-Analyzer
"{s.title}"

> Timespan
from {s.start_date.strftime('%b %d, %Y')} until {s.end_date.strftime('%b %d, %Y')}

> Timeline
message stats by...
\t - month = {s.message_count_by_month}
\t - day of week = {s.message_count_by_day_of_week}
\t - time of day = {s.message_count_by_time_of_day}
\t - participant = {s.message_count_by_participant}
\t - participant X month = {s.message_count_by_participant_and_month}

> Total numbers
days = {s.day_count}
messages = {s.message_count}
words = {s.word_count}
letters = {s.letter_count}

> Tops
most messages = {s.date_most_active_message[0].strftime('%b %d, %Y')} | {s.date_most_active_message[1]}
most media files = {s.date_most_active_media[0].strftime('%b %d, %Y')} | {s.date_most_active_media[1]}
most stickers = {s.date_most_active_sticker[0].strftime('%b %d, %Y')} | {s.date_most_active_sticker[1]}

> Averages
Average words per message = {s.get_average_words_per_message()}
Average letters per message = {s.get_average_letters_per_message()}
Average messages per day = {s.get_average_messages_per_day()}
Average letters per day = {s.get_average_letters_per_day()}

> Rich contents
rich content count = {s.rich_content_count}
rich content duration = {s.rich_content_duration}
"""