"""Provides a structure to store the statistics of the chat as an instance.

Stores the full statistics of the entire chatroom, or a simple metadata of a 
single chat. Includes an extensive set of getters for various types of
statistics.

  Typical usage example:

  foo = Chatroom()
  bar = foo.get_message_count()
"""
class Message:
    """A class used to represent a message in a chatroom.

    This class supports counting functions that can be used to create statistic
    values. Will be mostly used as a part of `kakaotalk.Chatroom` instance.

    Attributes:
        time: A datetime instance of the time which the message was sent.
        author: A string of the name of the participant who sent the message.
        content: A string of the content of the message.
        rich_content_type: A string indicating the type of rich content message.
    """
    time = None
    author = None
    content = None
    rich_content_type = None

    def __init__(self, time, author, content, rich_content_type) -> None:
        """Initializes Message with time, author, content and the type of the
           rich content.
        """
        self.time = time
        self.author = author
        self.content = content
        self.rich_content_type = rich_content_type

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
    message_count_by_day_of_week = {}  # {int: int} format, key 0 being Sunday
    message_count_by_time_of_day = {}  # {int: int} format, key 0 being 12AM
    message_count_by_participant = {}  # {'name': int} format

    day_count = 0
    word_count = 0
    letter_count = 0

    date_most_active_message = None  # (datetime, int) format
    date_most_active_media = None  # (datetime, int) format
    date_most_active_stickers =  None  # (datetime, int) format

    rich_content_count_photo = 0
    rich_content_count_video = 0
    rich_content_count_file = 0
    rich_content_count_link = 0
    rich_content_count_youtube_link = 0
    rich_content_count_stickers = 0
    rich_content_count_voice_note = 0
    rich_content_count_deleted = 0

    rich_content_count_voice_call = 0  # in seconds
    rich_content_count_live_talk = 0  # in seconds

    event_count_invite = 0
    event_count_leave = 0

    def __init__(self, title) -> None:
        self.title = title
    
    def add_message(msg: Message) -> None:
        return None

