def single_get_first(unicode1):
    str1 = unicode1.encode('gbk')
    try:
        ord(str1)
        return str1
    except:
        asc = str1[0] * 256 + str1[1] - 65536
        if asc >= -20319 and asc <= -20284:
            return 'a'
        if asc >= -20283 and asc <= -19776:
            return 'b'
        if asc >= -19775 and asc <= -19219:
            return 'c'
        if asc >= -19218 and asc <= -18711:
            return 'd'
        if asc >= -18710 and asc <= -18527:
            return 'e'
        if asc >= -18526 and asc <= -18240:
            return 'f'
        if asc >= -18239 and asc <= -17923:
            return 'g'
        if asc >= -17922 and asc <= -17418:
            return 'h'
        if asc >= -17417 and asc <= -16475:
            return 'j'
        if asc >= -16474 and asc <= -16213:
            return 'k'
        if asc >= -16212 and asc <= -15641:
            return 'l'
        if asc >= -15640 and asc <= -15166:
            return 'm'
        if asc >= -15165 and asc <= -14923:
            return 'n'
        if asc >= -14922 and asc <= -14915:
            return 'o'
        if asc >= -14914 and asc <= -14631:
            return 'p'
        if asc >= -14630 and asc <= -14150:
            return 'q'
        if asc >= -14149 and asc <= -14091:
            return 'r'
        if asc >= -14090 and asc <= -13119:
            return 's'
        if asc >= -13118 and asc <= -12839:
            return 't'
        if asc >= -12838 and asc <= -12557:
            return 'w'
        if asc >= -12556 and asc <= -11848:
            return 'x'
        if asc >= -11847 and asc <= -11056:
            return 'y'
        if asc >= -11055 and asc <= -10247:
            return 'z'
        return ''
 
arr = [
    ['a', 'b', 'c', 'd', 'e', 'f'],
    ['g', 'h', 'i', 'j', 'k', 'l'],
    ['m', 'n', 'o', 'p', 'q', 'r'],
    ['s', 't', 'u', 'v', 'w', 'x'],
    ['y', 'z', '', '', '', '']
]

class KeySearch():

    def __init__(self, lastValue):
        self.lastValue = lastValue

    def getKeys(self, string):
        if string == None:
            return None
        arr = []
        lst = list(string)    
        for l in lst:
            pos = self.getPosition(single_get_first(l))
            x = pos['x']
            y = pos['y']
            if x != 0:
                for i in range(abs(x)):
                    arr.append('left' if x > 0 else 'right')
            if y != 0:
                for i in range(abs(y)):
                    arr.append('up' if y > 0 else 'down')            
            arr.append('enter')
            # print(pos)
        arr.extend(self.getLastKeys())
        return arr

    # 计算最后字符的偏移量
    def getLastKeys(self):
        _list = []
        index = 0        
        for item in arr:
            if self.lastValue in item:
                i = len(item) - arr[index].index(self.lastValue) + 1
                for j in range(i):
                    _list.append('right')
                _list.append('down')
                _list.append('enter-2')
                _list.append('enter')
                return _list
            index += 1

    # 获取位置
    def getPosition(self, value):
        index = 0
        for item in arr:
            if self.lastValue in item:
                y1 = index
            if value in item:
                y2 = index
            index += 1
        x1 = arr[y1].index(self.lastValue)
        x2 = arr[y2].index(value)
        # print('上+ 下-', y1, y2, y1 - y2)
        # print('左+ 右-',x1, x2, x1 - x2)
        self.lastValue = value
        return {
            'x': x1 - x2,
            'y': y1 - y2
        }

# ks = KeySearch('o')
# print(ks.getKeys("大江大河"))