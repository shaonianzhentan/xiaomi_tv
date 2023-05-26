import aiohttp, json, time, hmac, socket, hashlib, os, re, datetime
from urllib.parse import urlencode, urlparse, parse_qsl

def check_port(ip, port):
    is_alive = True
    # 检测当前IP是否在线
    sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sk.settimeout(1)
    try:
        sk.connect((ip, port))
    except Exception:
        is_alive = False
    sk.close()
    return is_alive

# 获取执行命令
async def mitv_api(ip, url):
    try:
        request_timeout = aiohttp.ClientTimeout(total=1)
        async with aiohttp.ClientSession(timeout=request_timeout) as session:
            async with session.get(f'http://{ip}:6095/{url}') as response:
                data = json.loads(await response.text())
                return data
    except Exception as ex:
        print(ex)
    return None

# 启动应用
async def startapp(ip, packagename):
    return await mitv_api(ip, f'controller?action=startapp&type=packagename&packagename={packagename}')

# 发送按键
async def keyevent(ip, keycode):
    return await mitv_api(ip, f'controller?action=keyevent&keycode={keycode}')

# 获取电视信息
async def getsysteminfo(ip):
    res = await mitv_api(ip, f'controller?action=getsysteminfo')
    if res is not None:
        return res['data']

# 发送按键
async def changesource(ip, source):
    return await mitv_api(ip, f'controller?action=changesource&source={source}')

# 获取安装应用
async def getinstalledapp(ip):
    res = await mitv_api(ip, f'controller?action=getinstalledapp&count=999&changeIcon=1')
    if res is not None:
        return res['data']['AppInfo']       


''' 电视截屏 '''
def with_opaque(pms, token=None):
        '''
        参考代码：https://github.com/al-one/hass-xiaomi-miot/blob/master/custom_components/xiaomi_miot/media_player.py
        '''
        if token is None:
            token = '881fd5a8c94b4945b46527b07eca2431'
        _hmac_key = '2840d5f0d078472dbc5fb78e39da123e'
        pms.update({ 'timestamp': int(time.time() * 1000), 'token': token })
        pms['opaque'] = hmac.new(_hmac_key.encode(), urlencode(pms).encode(), hashlib.sha1).hexdigest()
        pms.pop('token', None)
        return pms

async def capturescreen(ip):
    params = with_opaque({'action': 'capturescreen', 'compressrate': 100})
    res = await mitv_api(ip, f'controller?{urlencode(params)}')
    if res is not None:
        rdt = res['data']
        # 获取图片
        token = rdt.get('token')
        params = with_opaque({'action': 'getResource', 'name': 'screenCapture'}, token)
        return {
            'url': f'http://{ip}:6095/request?{urlencode(params)}',
            'id': rdt.get('pkg'),
            'name': rdt.get('label')
        }

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

    def __init__(self, lastValue, type):
        self.lastValue = lastValue
        self.type = type

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
                i = len(item) - arr[index].index(self.lastValue)
                for j in range(i):
                    _list.append('right')
                # iqiyi、youku、qqtv
                if self.type == '1':
                    _list.append('right')
                    _list.append('enter-2')
                    _list.append('left')
                    _list.append('enter')
                else:
                    _list.append('down')
                    _list.append('right')
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


# 快捷键
ACTION_KEYS = {
    'sleep': ['power', 'right', 'enter'],
    'power': ['power'],
    'up': ['up'],
    'down': ['down'],
    'right': ['right'],
    'left': ['left'],
    'home': ['home'],
    'enter': ['enter'],
    'back': ['back'],
    'menu': ['menu'],
    'volumedown': ['volumedown'],
    'volumeup': ['volumeup'],
    # 开启调试模式（最后两个键是弹窗确定，第一次需要）
    'adb': [
        # 打开账号与安全
        'right', 'right', 'right', 'enter',
        # 选择ADB高度
        'down', 'down', 'enter', 
        # 选择开启
        'up', 'enter', 
        # 二次确定
        'down', 'left', 'enter']
}

async def open_app(ip, app_id):
    ''' 打开应用 '''
    await keyevent(ip, 'home')
    time.sleep(1)
    await startapp(ip, app_id)
    time.sleep(1)


async def send_keystrokes(ip, keystrokes):
    ''' 批量发送按键 '''
    try:
        for keystroke in keystrokes:
            wait = 1.5
            if '-' in keystroke:
                arr = keystroke.split('-')
                keystroke = arr[0]
                wait = float(arr[1])
            await keyevent(ip, keystroke)
            # print(res)
            # 如果是组合按键，则延时
            if len(keystrokes) > 1:
                time.sleep(wait)

    except Exception as ex:
        print(ex)