# 간단한 카카오톡 채팅 분석

```
chatting = chat(filename)

chatting.count_chat(['주창', '윤석찬'])      # 주창, 윤석찬이 채팅을 몇번 했는지 출력. (인자가 없을 시 전체 인원 채팅 횟수 출력)

chatting.count_word(['hey', 'Hey'])         # 'hey'와 'Hey'가 몇번 사용됬는지 출력
chatting.count_word(['ㅋㅋ'], 'c2w2m2')     # 'c2w2m2'가 'ㅋㅋ'를 몇번 사용했는지 출력

chatting.get_last_date()                    # 최종 채팅 날짜 반환 

chatting.get_date_data('2018-4-23-월')      # 해당 날짜의 채팅을 반환. 날짜 형식은 년-월-일-요일
```