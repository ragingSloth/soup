import re
import collections
from collections import defaultdict

class Soup(object):
    def __init__(self, d, prints=False):
        for k in d.keys():
            if isinstance(d[k], str) or isinstance(d[k], unicode):
                d[k] = d[k].replace('}','<R_BRACE>')
                d[k] = d[k].replace('{','<L_BRACE>')
                d[k] = d[k].replace(':','<COLON>')
        self.d = str(d).replace('}',' }')
        self.stream = filter(self.got_chars, self.d.split())
        self.lexer = Lexer(self.stream)
        self.lexer.lex()
        self.parser = Parser(self.lexer.tokens, d, prints=prints)
        #print self.reconstruct([1,('actors',['Keanu', 'Lawrence', ('lady','test')]),('rating', 9)])

    def got_chars(self, string, chars=['}', '{', ':']):
        for i in chars:
            if i in string:
                return True
        return False

    def reconstruct(self, structure):
        data = defaultdict()
        for item in structure:
            if not isinstance(item,tuple):
                val = self.parser.lut[item]
                if isinstance(val, str) or isinstance(val, unicode):
                    val = val.replace('<R_BRACE>','}')
                    val = val.replace('<L_BRACE>','{')
                    val = val.replace('<COLON>',':')
                data[item] = val
            elif isinstance(item[1],list):
                data[item[0]] = self.reconstruct(item[1])
            else:
                val = self.parser.lut[item[1]]
                if isinstance(val, str) or isinstance(val, unicode):
                    val = val.replace('<R_BRACE>','}')
                    val = val.replace('<L_BRACE>','{')
                    val = val.replace('<COLON>',':')
                data[item[0]] = val
        return dict(data)


class Lexer(object):
    def __init__(self, stream):
        self.s = stream
        self.tokens = []
        self.state = None

    def gen_token(self,t):
        token = []
        if t[0] == '{':
            token.append('T_OPEN')
            r = re.compile('(\'?[-_a-zA-Z0-9]+?\'?):')
            key = r.search(t)
            token.append('T_KEY')
            token.append(key.group(1))
        elif '}' in t:
            n_close = t.count('}')
            token += n_close*['T_CLOSE']
        else:
            r = re.compile('(\'?[-_a-zA-Z0-9]+?\'?):')
            key = r.search(t)
            token.append('T_KEY')
            token.append(key.group(1))
        return token

    def lex(self):
        if self.s == []:
            return
        token = self.s[0]
        self.tokens += self.gen_token(token)
        self.s = self.s[1:]
        self.lex()

class Parser(object):
    def __init__(self, ts, d, prints=True):
        self.ts = ts
        ts = self.expect_OPEN(ts)
        if ts == None:
            print 'Error, that\'s definitely not a dictionary, to be honest I\'m mostly just impressed that you didn\'t break the lexer or some other bit, good job'
        else:
            self.ts = ts
            self.data = self.parse_dictionary(self.ts, d)
            if prints:
                self.pretty_print(self.data)
                print 88*'='
            self.lut = dict(list(self.flatten(self.data)))

    def expect_OPEN(self, ts):
        if ts[0] == 'T_OPEN':
            return ts[1:]
        else:
            return None

    def expect_CLOSE(self, ts):
        if ts[0] == 'T_CLOSE':
            return ts[1:]
        else:
            return None

    def expect_KEY(self, ts):
        if ts[0] == 'T_KEY':
            if '\'' in ts[1]:
                return ts[1].replace("'",''),ts[2:]
            else:
                return int(ts[1]),ts[2:]
        else:
            return None, ts

    #pass in dictionary and just make the key value pairs on the fly
    def parse_dictionary(self,ts,d):
        data = []
        while True:
            key, ts = self.expect_KEY(ts)
            if key == None:
                tsn = self.expect_OPEN(ts)
                if tsn == None:
                    tsn = self.expect_CLOSE(ts)
                    if tsn == None:
                        print 'Error'
                        break
                    else:
                        if tsn == []:
                            return data
                        else:
                            return data, tsn
                else:
                    ret, ts = self.parse_dictionary(tsn, d[data[-1][0]])
                    data.append(ret)
            else:
                data.append((key, d[key]))

    def pretty_print(self,data,depth=0):
        for i in xrange(len(data)):
            if type(data[i]) != type([]):
                print depth*'---->'+str(data[i])
            else:
                self.pretty_print(data[i],depth=depth+1)

    def flatten(self, l):
        for i in l:
            if isinstance(i,list):
                for sub in self.flatten(i):
                    yield sub
            else:
                yield i

#TODO same key twice
if __name__ == '__main__':
    d = {'a':1, 'b':2, 'c':3}
    tree = Soup(d,prints=True)
    s = [('A', 'a'), ('B', ['b']), 'c']
    print tree.reconstruct(s)
