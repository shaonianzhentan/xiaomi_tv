import sys, re, os, requests

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
            group = '默认'
            matchObj = re.match(r'(.*)group-title="(.+)"', info)
            if matchObj is not None:
                group = matchObj.group(2)
            song=track(group,title,None)
        elif (len(line) != 0):
            # pull song path from all other, non-blank lines
            song.path=line
            playlist.append(song)
            # reset the song variable so it doesn't use the same EXTINF more than once
            song=track(None,None,None)

    infile.close()

    return playlist

# 直播源文件
m3ufile = 'tv.m3u'

def update_tvsource(m3u_url):
    if m3u_url == '':
        return
    # 下载文件
    res = requests.get(url=m3u_url)
    with open(m3ufile,"wb") as fs:
        fs.write(res.content)

# 读取文件
def get_tvsource():
    if os.path.exists(m3ufile) == False:
        return {}
    # 判断文件是否存在
    playlist = parseM3U(m3ufile)
    playsource = {}
    for track in playlist:
        # print (track.title, track.group, track.path)
        if track.group is None:
            continue
        if track.group not in playsource:
            playsource[track.group] = []
        playsource[track.group].append((track.title, track.path))
    return playsource

'''
playsource = get_playsource('https://raw.githubusercontent.com/reysc/M3U8/master/all.m3u')
for item in playsource:
    print(item)
'''