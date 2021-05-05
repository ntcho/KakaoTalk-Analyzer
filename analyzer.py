"""Parses and returns the statistics of the chat.

Reads the given file and accumulates the statistics while reading throughout 
the chat log. Content of the file and strings used in this module will be
UTF-8 encoded.

  Typical usage example:

  foo = analyze("data.txt")
  bar = foo.get_chat_count()
"""


from kakaotalk import Chatroom, Message, Event

import re
import datetime
import logging as log

log.basicConfig(level=log.INFO)
# log.basicConfig(level=log.WARNING)


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

en_rich_content_photo = 'Photo'
en_rich_content_video = 'videos'
en_rich_content_file = 'File: .+'
en_rich_content_link = 'http.+|www\\..+'
en_rich_content_youtube_link = 'http.+youtu.+'
en_rich_content_stickers = 'Emoticons'
en_rich_content_voice_call = 'Voice Call (\d+):(\d+)'
                             # group(1): minute
                             # group(2): second
en_rich_content_voice_call_hr = 'Voice Call (\d+):(\d+):(\d+)' # voice call > 1h
                                # group(1): hour
                                # group(2): minute
                                # group(3): second
en_rich_content_video_call = 'Video Call (\d+):(\d+)'
                             # group(1): minute
                             # group(2): second
en_rich_content_video_call_hr = 'Video Call (\d+):(\d+):(\d+)' # video call > 1h
                                # group(1): hour
                                # group(2): minute
                                # group(3): second
en_rich_content_live_talk = 'Live Talk ended (\d+):(\d+)'
                            # group(1): minute
                            # group(2): second
en_rich_content_live_talk_hr = 'Live Talk ended (\d+):(\d+):(\d+)' # live talk > 1h
                               # group(1): hour
                               # group(2): minute
                               # group(3): second
en_rich_content_voice_note = 'Voice Note'
en_rich_content_deleted = 'This message was deleted.'

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

ko_rich_content_photo = '사진'
ko_rich_content_video = '동영상'
ko_rich_content_file = '파일: .+'
ko_rich_content_link = 'http.+|www\\..+'
ko_rich_content_youtube_link = 'http.+youtu.+'
ko_rich_content_stickers = '이모티콘'
ko_rich_content_voice_call = 'Voice Call (\d+):(\d+)'
                             # group(1): minute
                             # group(2): second
ko_rich_content_voice_call_hr = 'Voice Call (\d+):(\d+):(\d+)' # voice call > 1h
                                # group(1): hour
                                # group(2): minute
                                # group(3): second
ko_rich_content_video_call = 'Video Call (\d+):(\d+)'
                             # group(1): minute
                             # group(2): second
ko_rich_content_video_call_hr = 'Video Call (\d+):(\d+):(\d+)' # video call > 1h
                                # group(1): hour
                                # group(2): minute
                                # group(3): second
ko_rich_content_live_talk = 'Live Talk ended (\d+):(\d+)'
                            # group(1): minute
                            # group(2): second
ko_rich_content_live_talk_hr = 'Live Talk ended (\d+):(\d+):(\d+)' # live talk > 1h
                               # group(1): hour
                               # group(2): minute
                               # group(3): second
ko_rich_content_voice_note = 'Voice Note'
ko_rich_content_deleted = '삭제된 메시지입니다.'

ko_event_invite = '(.{,20})님이 (.+)님을 초대하였습니다\\.'
                  # group(1): inviter
                  # group(2): invitee (could be a list of names)
ko_event_leave = '(.{,20})님이 나갔습니다\\.'
                 # group(1): left participant

# list of rich content types that don't require regex
# used to iterate through to check all rich content types
# ordered high-to-low in frequency of appearance in normal chat
rich_content_types = [
    'stickers', 
    'photo', 
    'video', 
    'deleted'
    'voice_note', 
    ]

# list of rich content types that require regex
rich_content_regex_types = [
    'youtube_link', 
    'link', 
    'file',
    ]

# list of rich content types that require regex and also includes duration
rich_content_regex_duraton_types = [
    'voice_call', 
    'video_call', 
    'voice_call_hr', 
    'video_call_hr', 
    'live_talk', 
    'live_talk_hr', 
    ]

# list of date tag format to be used in datetime.strptime() by locale
date_tag_format = {
    'en': '%B %m, %Y',
    'ko': '%Y년 %m월 %d일'
}

# list of locales supported
locales = ['en', 'ko']

# hours that has to be added depending on the locale
locale_hours = {
    'en': {
        'A': 0, 'P': 12  # 3AM becomes 3, 3PM becomes 3 + 12 = 15
    },
    'ko': {
        '전': 0, '후': 12 # 오전 3시 becomes 3, 오후 3시 becomes 3 + 12 = 15
    }
}

# group index of time format for each locales
locale_time_format = {
    'en': {  # see en_message
        'ampm': 4,
        'hour': 2,
        'minute': 3
    },
    'ko': {  # see ko_message
        'ampm': 2,
        'hour': 3,
        'minute': 4
    }
}

# used for regex matching, by locale
match = {
    'en': {
        'metadata': {
            1: en_metadata_1,
            2: en_metadata_2
        },
        'date_tag': en_date_tag,
        'message': en_message,
        'rich_content': {
            'photo': en_rich_content_photo,
            'video': en_rich_content_video,
            'file': en_rich_content_file,
            'link': en_rich_content_link,
            'youtube_link': en_rich_content_youtube_link,
            'stickers': en_rich_content_stickers,
            'voice_call': en_rich_content_voice_call,
            'video_call_hr': en_rich_content_video_call_hr,
            'video_call': en_rich_content_video_call,
            'video_call_hr': en_rich_content_video_call_hr,
            'live_talk': en_rich_content_live_talk,
            'live_talk_hr': en_rich_content_live_talk_hr,
            'voice_note': en_rich_content_voice_note,
            'deleted': en_rich_content_deleted,
        },
        'event': {
            'invite': en_event_invite,
            'leave': en_event_leave
        }
    },
    'ko': {
        'metadata': {
            1: ko_metadata_1,
            2: ko_metadata_2
        },
        'date_tag': ko_date_tag,
        'message': ko_message,
        'rich_content': {
            'photo': ko_rich_content_photo,
            'video': ko_rich_content_video,
            'file': ko_rich_content_file,
            'link': ko_rich_content_link,
            'youtube_link': ko_rich_content_youtube_link,
            'stickers': ko_rich_content_stickers,
            'voice_call': ko_rich_content_voice_call,
            'voice_call_hr': ko_rich_content_voice_call_hr,
            'video_call': ko_rich_content_video_call,
            'video_call_hr': ko_rich_content_video_call_hr,
            'live_talk': ko_rich_content_live_talk,
            'live_talk_hr': ko_rich_content_live_talk_hr,
            'voice_note': ko_rich_content_voice_note,
            'deleted': ko_rich_content_deleted,
        },
        'event': {
            'invite': ko_event_invite,
            'leave': ko_event_leave
        }
    }
}


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

    title = None
    date_saved = None
    start_date = None
    end_date = None

    chatroom = None

    # Locale of the chat log
    lc = None

    # Read from file
    with open(file_name, 'r', encoding='UTF-8') as f:
        try:
            # Compare first line with metadata_1
            metadata_1 = f.readline()

            # Determine chat locale
            for l in locales:
                match_title = re.match(match[l]['metadata'][1], metadata_1)
                if match_title is not None:
                    # Locale match found, set it as the current locale
                    lc = l
                    title = match_title.group(1)
                    break
            
            if lc is None:
                raise ValueError('locale not supported or format not recognized')

            # Parse metadata_2
            metadata_2 = f.readline()

            match_date_saved = re.match(match[lc]['metadata'][2], metadata_2)
            date_saved = datetime.strptime(
                match_date_saved.group(1), 
                '%Y-%m-%d %H:%M:%S')
            
            # Initialize Chatroom instance
            chatroom = Chatroom(title, date_saved)

            f.readline() # skip empty new line before the chat log starts
        
        except ValueError as err:
            log.error(err)
        except:
            log.error('cannot read the metadata of the file')
        
        try:
            if chatroom is None:
                raise ValueError('kakaotalk.Chatroom is not initialized')
            
            # Temporary variable to hold re.match() results
            matches = None

            # Read the whole file
            for line in f:

                # 1. Message match
                matches = re.match(match[lc]['message'], line)
                if matches is not None and matches.group(1) is not None:

                    # Calculate datetime
                    time = None
                    if end_date is not None:
                        # (original hour) + (0 or 12 hour depending on the indicator)
                        hour = int(matches.group(locale_time_format[lc]['hour']))\
                               + locale_hours[lc][matches.group(
                                   locale_time_format[lc]['ampm'])]
                        minute = int(matches.group(locale_time_format[lc]['minute']))
                        # datetime object with updated hour and minute
                        time = end_date.replace(hour=hour, minute=minute)

                    # Check whether the message contains rich content
                    rich_content_type = None
                    rich_content_duration = None
                    rc_matches = None

                    # Check rich contents that don't need regex (most frequent)
                    for rc_type in rich_content_types:
                        if matches.group(5) == match[lc]['rich_content'][rc_type]:
                            rich_content_type = rc_type
                            break

                    if rich_content_type is None:
                        # Check rich contents that needs regex (less frequent)
                        for rc_type in rich_content_regex_types:
                            rc_matches = re.match(match[lc]['rich_content'][rc_type])
                            if rc_matches is not None and rc_matches.group(1) is not None:
                                rich_content_type = rc_type
                                break
                    
                    if rich_content_type is None:
                        # Check rich contents that needs regex and has duration (least frequent)
                        for rc_type in rich_content_regex_duraton_types:
                            rc_matches = re.match(match[lc]['rich_content'][rc_type])
                            if rc_matches is not None and rc_matches.group(1) is not None:
                                rich_content_type = rc_type

                                # Duration is shorter than 1 hour
                                if 'hr' not in rc_type:
                                    rich_content_duration = int(rc_matches.group(1)) * 60\
                                                            + int(rc_matches.group(2))
                                # Duration is longer than 1 hour
                                else:
                                    rich_content_duration = int(rc_matches.group(1)) * 60 * 60\
                                                            + int(rc_matches.group(2)) * 60\
                                                            + int(rc_matches.group(3))
                    
                    if rich_content_type is not None:
                        log.info(f'Rich content found: type={rich_content_type}')
                    if rich_content_duration is not None:
                        log.info(f'Rich content duration found: duration={rich_content_duration}')

                    # Create Message instance and add to Chatroom
                    chatroom.add_message(Message(
                        time,
                        matches.group(1),  # author
                        matches.group(5),  # content 
                        rich_content_type,
                        rich_content_duration
                    ))
                    continue
                
                # 2. Date tag match
                matches = re.match(match[lc]['date_tag'], line)
                if matches is not None and matches.group(1) is not None:
                    date = datetime.strptime(matches.group(1), date_tag_format[lc])

                    # Update start_date on first date tag
                    if start_date is None:
                        start_date = date
                    
                    # Update end_date in order to set message dates
                    end_date = date
                    continue
                
                # 3. Event match
                is_event = False

                for event_type in ['invite', 'leave']:
                    matches = re.match(match[lc]['event'][event_type], line)
                    if matches is not None and matches.group(1) is not None:
                        # Create Event instance and add to Chatroom
                        chatroom.add_event(Event(event_type, line))
                        is_event = True
                        log.info(f'Event found: type={event_type}')
                        break
                
                # 4. Multi-line message match
                if is_event is False and len(chatroom.messages) > 0:
                    # Append the line to the last message instance
                    chatroom.messages[-1].append(line)
                        
        except ValueError as err:
            log.error(err)
        except:
            log.error('cannot parse the given chat log')
