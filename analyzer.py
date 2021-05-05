"""Parses and returns the statistics of the chat.

Reads the given file and accumulates the statistics while reading throughout 
the chat log. Content of the file and strings used in this module will be
UTF-8 encoded.

  Typical usage example:

  foo = analyze("data.txt")
  bar = foo.get_chat_count()
"""


import re
import logging as log

log.basicConfig(level=log.INFO)
# log.basicConfig(level=log.WARNING)


def analyze(file_name: str):
    """Parses the chat log and returns a kakaotalk.Chatroom instance.

    Args:
        file_name (str): A string of file name to parse from. Should be located
          in the same directory as the executable.

    Returns:
        A kakaotalk.Chatroom instance with the corresponding values.

    Raises:
        IOError: An error occurred reading the file.
        ValueError: An error occurred parsing the file.
    """
    # Split date tags and chats
    log.info('Splitting text data...')

    '''
    KakaoTalk chat export format (v3.2.6.2748, May 2021) - English locale

    {title} with KakaoTalk Chats                                  # Metadata 1
    Date Saved: {YYYY}-{MM}-{DD} {HH}:{MM}:{SS}                   # Metadata 2

    --------------- {Day}, {Month} {dd}, {YYYY} ---------------   # Date tag
    [{participant}] [{hh}:{MM} {A/PM}] {multi-line message}       # Message
    ...
    [{participant}] [{hh}:{MM} {A/P}M] Photo                      # Photo
    [{participant}] [{hh}:{MM} {A/P}M] videos                     # Video
    [{participant}] [{hh}:{MM} {A/P}M] File: {file name}          # File
    [{participant}] [{hh}:{MM} {A/P}M] http{link}                 # Link
    [{participant}] [{hh}:{MM} {A/P}M] https://youtu{link}        # YT link
    [{participant}] [{hh}:{MM} {A/P}M] Emoticons                  # Stickers
    [{participant}] [{hh}:{MM} {A/P}M] Voice Call {hh:mm:ss}      # Voice call
    [{participant}] [{hh}:{MM} {A/P}M] Video Call {hh:mm:ss}      # Video call
    [{participant}] [{hh}:{MM} {A/P}M] Live Talk ended {hh:mm:ss} # Live Talk
    [{participant}] [{hh}:{MM} {A/P}M] Voice Note                 # Voice note
    [{participant}] [{hh}:{MM} {A/P}M] This message was deleted.  # Deleted message

    {participant} invited {participant}.                          # Invite event
    {participant} left.                                           # Leave event
    '''

    en_metadata_1 = '(.{,50}) with KakaoTalk Chats'
                    # group(1): chatroom title
    en_metadata_2 = 'Date Saved: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
                    # group(1): chat export timestamp
                    # - parse with strptime(match, '%Y-%m-%d %H:%M:%S')

    en_date_tag = '--------------- \w+, (\w+ \d{,2}, \d{4}) ---------------'
                  # group(1): date tag
                  # - parse with strptime(match, '%B %m, %Y')
    en_message = '\\[(.{,20})\\] \\[(\d{,2}):(\d{2}) (\w)M\\] (.*)'
                 # group(1): participant name
                 # group(2): hour (12H format)
                 # group(3): minute
                 # group(4): A or P for AM and PM each
                 # group(5): message content
                 # TODO: add multi-line message match support

    en_message_photo = 'Photo'
    en_message_video = 'videos'
    en_message_file = 'File: .+'
    en_message_link = 'http.+|www\\..+'
    en_message_youtube_link = 'http.+youtu.+'
    en_message_stickers = 'Emoticons'
    en_message_voice_call = 'Voice Call (\d+):(\d+)'
                            # group(1): minute
                            # group(2): second
    en_message_voice_call_hr = 'Voice Call (\d+):(\d+):(\d+)' # voice call > 1h
                               # group(1): hour
                               # group(2): minute
                               # group(3): second
    en_message_live_talk = 'Live Talk ended (\d+):(\d+)'
                           # group(1): minute
                           # group(2): second
    en_message_live_talk_hr = 'Live Talk ended (\d+):(\d+):(\d+)' # live talk > 1h
                              # group(1): hour
                              # group(2): minute
                              # group(3): second
    en_message_voice_note = 'Voice Note'
    en_message_deleted = 'This message was deleted.'

    en_event_invite = '(.{,20}) invited (.+)\\.'
                      # group(1): inviter
                      # group(2): invitee (could be a list of names)
    en_event_leave = '(.{,20}) left\\.'
                     # group(1): left participant

    '''
    KakaoTalk chat export format (v3.2.6.2748, May 2021) - Korean locale

    {title} 님과 카카오톡 대화                                        # Metadata 1
    저장한 날짜 : {YYYY}-{MM}-{DD} {HH}:{MM}:{SS}                    # Metadata 2

    --------------- {YYYY}년 {mm}월 {dd}일 {day}요일 --------------- # Date tag
    [{participant}] [오{전/후} {hh}:{MM}] {multi-line message}      # Message
    ...
    [{participant}] [오{전/후} {hh}:{MM}] 사진                       # Photo
    [{participant}] [오{전/후} {hh}:{MM}] 동영상                     # Video
    [{participant}] [오{전/후} {hh}:{MM}] 파일: {file name}          # File
    [{participant}] [오{전/후} {hh}:{MM}] http{link}                # Link
    [{participant}] [오{전/후} {hh}:{MM}] https://youtu{link}       # YT link
    [{participant}] [오{전/후} {hh}:{MM}] 이모티콘                    # Stickers
    [{participant}] [오{전/후} {hh}:{MM}] TODO                      # Voice call
    [{participant}] [오{전/후} {hh}:{MM}] TODO                      # Video call
    [{participant}] [오{전/후} {hh}:{MM}] TODO                      # Live Talk
    [{participant}] [오{전/후} {hh}:{MM}] TODO                      # Voice note
    [{participant}] [오{전/후} {hh}:{MM}] 삭제된 메시지입니다.         # Deleted message

    {participant}님이 {participant}님을 초대하였습니다.                # Invite event
    {participant}님이 나갔습니다.                                     # Leave event
    '''

    ko_metadata_1 = '(.{,50}) 님과 카카오톡 대화'
                    # group(1): chatroom title
    ko_metadata_2 = '저장한 날짜 : (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
                    # group(1): chat export timestamp
                    # - parse with strptime(match, '%Y-%m-%d %H:%M:%S')

    ko_date_tag = '--------------- (\d{4}년 \d{,2}월 \d{,2}일) .요일 ---------------'
                  # group(1): date tag
                  # - parse with strptime(match, '%Y년 %m월 %d일')
    ko_message = '\\[(.{,20})\\] \\[오(\w) (\d{,2}):(\d{2})\\] (.*)'
                 # group(1): participant name
                 # group(2): '전' or '후' for AM and PM each
                 # group(3): hour (12H format)
                 # group(4): minute
                 # group(5): message content
                 # TODO: add multi-line message match support

    ko_message_photo = '사진'
    ko_message_video = '동영상'
    ko_message_file = '파일: .+'
    ko_message_link = 'http.+|www\\..+'
    ko_message_youtube_link = 'http.+youtu.+'
    ko_message_stickers = '이모티콘'
    ko_message_voice_call = 'Voice Call (\d+):(\d+)'
                            # group(1): minute
                            # group(2): second
    ko_message_voice_call_hr = 'Voice Call (\d+):(\d+):(\d+)' # voice call > 1h
                               # group(1): hour
                               # group(2): minute
                               # group(3): second
    ko_message_live_talk = 'Live Talk ended (\d+):(\d+)'
                           # group(1): minute
                           # group(2): second
    ko_message_live_talk_hr = 'Live Talk ended (\d+):(\d+):(\d+)' # live talk > 1h
                              # group(1): hour
                              # group(2): minute
                              # group(3): second
    ko_message_voice_note = 'Voice Note'
    ko_message_deleted = '삭제된 메시지입니다.'

    ko_event_invite = '(.{,20})님이 (.+)님을 초대하였습니다\\.'
                      # group(1): inviter
                      # group(2): invitee (could be a list of names)
    ko_event_leave = '(.{,20})님이 나갔습니다\\.'
                     # group(1): left participant