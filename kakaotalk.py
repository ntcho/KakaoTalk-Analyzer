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
        
    def __init__(self, filename):
        f = open(filename, 'r', encoding='UTF8')
        self.data = f.read()
        f.close()

if __name__ == '__main__':
    count = chat('kakaotalk.txt')
    count.count_word('ㅋㅋ')
    count.count_word('ㅋㅋ', '주창')
    