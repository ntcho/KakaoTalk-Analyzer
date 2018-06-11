#-*- coding: utf-8 -*-

class chat:
    def parse_user(self, data):
        res = data[1:data.find("]")]
        return res

    def count_chat(self):
        res = dict()
        data = self.data
        data = data.split('\n')

        for i in data:
            try:
                if i[0] == '[':
                    res[self.parse_user(i)] += 1
            except KeyError:
                res[self.parse_user(i)] = 1
            except:
                pass

        for i in res.keys():
            print("[%s] : %d" % (i, res[i]))

    def count_word(self, word, name=''):
        data = self.data
        data = data.split('\n')

        count = 0

        if name == '':
            for i in data:
                count += i.count(word)
            print("[%s] : %d" % (word, count))
        else:
            for i in data:
                try:
                    if i[0] == '[':
                        if self.parse_user(i) == name:
                            count += i.count(word)
                except:
                    pass
            print("[%s's %s] : %d" % (name, word, count))
    
    def parse_last_date(self):
        data = self.data
        pivot = data.rfind("---------------")
        date = data[pivot - 17: pivot]
        print("[%s]" % date.strip())

    def get_date_data(self, date):
        date = date.split('-')
        date = "--------------- %s년 %s월 %s일 %s요일 ---------------" % (date[0], date[1], date[2], date[3])
        print(date)
        data = self.data
        data = data[data.find(date):]
        data = data.split('\n')
        flag = 0
        pData = []
        for i in data:
            if (flag == 0) and (date in i):
                flag = 1
                continue
            elif (flag == 1) and ('---------------' in i):
                break
            if flag == 1:
                pData.append(i)
        return pData

    def __init__(self, filename):
        f = open(filename, 'r', encoding='UTF8')
        self.data = f.read()
        f.close()

if __name__ == '__main__':
    count = chat('kakaotalk.txt')
    count.get_date_data('2018-4-23-월')
