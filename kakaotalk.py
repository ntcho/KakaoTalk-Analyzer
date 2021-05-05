"""Provides a structure to store the statistics of the chat as an instance.

Stores the full statistics of the entire chatroom, or a simple metadata of a 
single chat. Includes an extensive set of getters for various types of
statistics.

  Typical usage example:

  foo = Chatroom()
  bar = foo.get_chat_participant()
"""

class Chatroom:
    """A class used to represent a KakaoTalk chatroom.

    An object of this class will contain all the statistic information about
    the chatroom including number of chats, number of participants, and many
    more.

    Attributes:
        title: A string of the title of the chatroom provided in the chat log.
        date_saved: A timestamp of the date which the chat log was saved.
        chats: A list of kakaotalk.Chat instances.
        events: A list of kakaotalk.Event instances.
        start_date: A date of the first chat in the chatroom.
        end_date: A date of the last chat in the chatroom.

    """