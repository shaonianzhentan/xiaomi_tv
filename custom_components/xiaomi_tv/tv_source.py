import sys, re, os, aiohttp, time

class TVSource():

    def __init__(self) -> None:
        self.playlist = []
        self.groups = []
        self.update_time = None

    # 更新TV源
    async def update(self):
        # 缓存一小时
        if self.update_time is not None and (time.time() - self.update_time) < 3600:
            return

        m3ufile = 'xiaomi_tv.m3u'
        m3u_url = 'https://ghproxy.com/https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u'
        # 下载文件
        request_timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=request_timeout) as session:
            async with session.get(m3u_url) as response:
                with open(m3ufile,"wb") as fs:
                    fs.write(await response.read())
        # 判断文件是否存在
        playlist = parseM3U(m3ufile)
        self.playlist = playlist
        # 分组
        self.groups = list(set(map(lambda x: x.group, playlist)))

        self.update_time = time.time()

    def search_channel(self, name):
        # 频道搜索
        arr = list(filter(lambda x: name in x.title, self.playlist))
        print(arr)
        if len(arr) > 0:
            return arr[0].path

class track():
    def __init__(self, group, title, path):
        self.group = group
        self.title = title
        self.path = path

def parseM3U(infile):
    try:
        assert(type(infile) == '_io.TextIOWrapper')
    except AssertionError:
        infile = open(infile,'r')

    """
        All M3U files start with #EXTM3U.
        If the first line doesn't start with this, we're either
        not working with an M3U or the file we got is corrupted.
    """

    line = infile.readline()
    if not line.startswith('#EXTM3U'):
       return

    # initialize playlist variables before reading file
    playlist=[]
    song=track(None,None,None)

    for line in infile:
        line=line.strip()
        if line.startswith('#EXTINF:'):
            # pull length and title from #EXTINF line
            info,title=line.split('#EXTINF:')[1].split(',',1)
            #matchObj = re.match(r'(.*)status="online"', info)
            #if matchObj is None:
            #    continue
            group = '默认列表'
            if 'CCTV' in title:
                group = 'CCTV'
            elif 'NewTV' in title:
                group = 'NewTV'
            elif 'SiTV' in title:
                group = 'SiTV'
            elif '电影' in title or '影视' in title or '影視' in title or '视频' in title:
                group = '电影视频'
            elif '新闻' in title or '新聞' in title or '资讯' in title:
                group = '新闻资讯'
            elif '少儿' in title or '卡通' in title:
                group = '少儿卡通'
            elif '卫视' in title or '衛視' in title:
                group = '卫视'
            elif '上海' in title:
                group = '上海'
            elif '浙江' in title:
                group = '浙江'
            elif '江苏' in title:
                group = '江苏'
            elif '中国' in title or '中文' in title:
                group = '中文频道'
            song=track(group,title,None)
        elif (len(line) != 0):
            # pull song path from all other, non-blank lines
            song.path=line
            if song.group is not None:
                playlist.append(song)
            # reset the song variable so it doesn't use the same EXTINF more than once
            song=track(None,None,None)

    infile.close()

    return playlist