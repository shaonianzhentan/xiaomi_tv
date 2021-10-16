"""Add support for the Xiaomi TVs."""
import logging
from types import resolve_bases
import aiohttp, json, time, hmac, socket, hashlib
from urllib.parse import urlencode, urlparse, parse_qsl

import voluptuous as vol

from async_upnp_client import UpnpFactory, UpnpError
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.profiles.dlna import DmrDevice, TransportState


from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_STEP,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_SELECT_SOUND_MODE,
    SUPPORT_PLAY_MEDIA,
    SUPPORT_PLAY,
    SUPPORT_PAUSE,
    SUPPORT_NEXT_TRACK,
    SUPPORT_PREVIOUS_TRACK
)
from homeassistant.const import CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON, STATE_PLAYING, STATE_PAUSED, STATE_IDLE, STATE_UNAVAILABLE
import homeassistant.helpers.config_validation as cv

from .const import DEFAULT_NAME
from .utils import keyevent, startapp

_LOGGER = logging.getLogger(__name__)

SUPPORT_XIAOMI_TV = SUPPORT_VOLUME_STEP | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE | SUPPORT_SELECT_SOUND_MODE | \
    SUPPORT_PLAY_MEDIA | SUPPORT_PLAY | SUPPORT_PAUSE | SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK

# No host is needed for configuration, however it can be set.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Xiaomi TV platform."""

    # If a hostname is set. Discovery is skipped.
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    add_entities([XiaomiTV(host, name, hass)])

class XiaomiTV(MediaPlayerEntity):
    """Represent the Xiaomi TV for Home Assistant."""

    def __init__(self, ip, name, hass):
        """Receive IP address and name to construct class."""
        self.hass = hass
        self.ip = ip
        self._name = name
        self._volume_level = 1
        self._is_volume_muted = False
        self._state = STATE_OFF
        self.is_alive = False
        self._source_list = []
        self._sound_mode_list = []
        self.dlna_device = None
        # 已知应用列表
        self.app_list = []
        self.apps = {
                # '云视听极光': 'com.ktcp.video',
                # '芒果TV': 'com.hunantv.license',
                # '银河奇异果': 'com.gitvdemo.video',
                # 'CIBN酷喵': 'com.cibn.tv',
                # '视频头条': 'com.duokan.videodaily',
                # '小米通话': 'com.xiaomi.mitv.tvvideocall',
                # 'QQ音乐': 'com.tencent.qqmusictv',
                # '定时提醒': 'com.mitv.alarmcenter',
                # '天气': 'com.xiaomi.tweather',
                # '用户手册': 'com.xiaomi.mitv.handbook',
                # '桌面': 'com.mitv.tvhome',
                # '电视管家': 'com.xiaomi.mitv.tvmanager',
                # '日历': 'com.xiaomi.mitv.calendar',
                # '小爱同学': 'com.xiaomi.voicecontrol',
                # '相册': 'com.mitv.gallery',
                # '电视设置': 'com.xiaomi.mitv.settings',
                # '时尚画报': 'com.xiaomi.tv.gallery',
                # '无线投屏': 'com.xiaomi.mitv.smartshare'
            }
        # mitv ethernet Mac address
        self._attributes = {}

    @property
    def name(self):
        """Return the display name of this TV."""
        return self._name

    @property
    def unique_id(self):
        return self.ip.replace('.', '')

    @property
    def volume_level(self):
        return self._volume_level

    @property
    def is_volume_muted(self):
        return self._is_volume_muted

    @property
    def state(self):
        """Return _state variable, containing the appropriate constant."""
        return self._state

    @property
    def assumed_state(self):
        """Indicate that state is assumed."""
        return True

    @property
    def sound_mode_list(self):
        return self._sound_mode_list

    @property
    def source_list(self):
        return self._source_list

    @property
    def media_duration(self):
        if not self.dlna_device:
            return None
        return self.dlna_device.media_duration

    @property
    def media_position(self):
        if not self.dlna_device:
            return None
        return self.dlna_device.media_position

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_XIAOMI_TV

    @property
    def device_class(self):
        return 'tv'

    @property
    def extra_state_attributes(self):
        return self._attributes

    # 更新属性
    async def async_update(self):
        _len = len(self.app_list)
        # 检测当前IP是否在线
        sk = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sk.settimeout(1)
        try:
            sk.connect((self.ip, 6095))
            # print("server port connect OK! ")
            # 如果配置了dlna，则判断dlna设备的状态
            self._state = STATE_PLAYING
            dlna = self.dlna_device
            if dlna is not None:
                if dlna.transport_state in (
                    TransportState.PLAYING,
                    TransportState.TRANSITIONING,
                ):
                    self._state = STATE_PLAYING
                elif dlna.transport_state in (
                    TransportState.PAUSED_PLAYBACK,
                    TransportState.PAUSED_RECORDING,
                ):
                    self._state = STATE_PAUSED
                # 重新连接DLNA服务
                if self.is_alive == False:
                    await self.create_dlna_device()
            self.is_alive = True
            if _len == 0:
                res = await self.getsysteminfo()
                if res is not None:
                    await self.get_apps()
                    await self.create_dlna_device()
            # 获取截图
            await self.capturescreen()
        except Exception:
            # print("server port not connect!")
            self.is_alive = False
            self._state = STATE_OFF
            if _len > 0:
                self.app_list = []
        # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        sk.close()

    # 选择应用
    async def async_select_source(self, source):
        if self.apps[source] is not None:
            # 在选择应用时，先回到首页
            await self.keyevent('home')
            time.sleep(1)
            await self.execute('startapp&type=packagename&packagename=' + self.apps[source])

    # 选择数据源
    async def async_select_source_mode(self, mode):
        if self.sound_mode_list.count(mode) > 0:
            await self.execute('changesource&source=' + mode)

    async def async_turn_off(self):
        if self._state != STATE_OFF:
            await self.keyevent('power')
            self.fire_event('off')
            self._state = STATE_OFF

    async def async_turn_on(self):
        """Wake the TV back up from sleep."""
        if self._state != STATE_ON:
            self.fire_event('on')
            self._state = STATE_ON

    async def async_volume_up(self):
        await self.keyevent('volumeup')

    async def async_volume_down(self):
        await self.keyevent('volumedown')

    async def async_mute_volume(self, mute):
        if mute:
            await self.async_set_volume_level(0)
        else:
            await self.async_set_volume_level(0.5)
        self._is_volume_muted = mute

    async def async_set_volume_level(self, volume):
        self._volume_level = volume
        dlna = self.dlna_device
        if dlna is not None:
            # 兼容小米电视音量控制
            if volume <= 0.15:
                arr = [0, 0.05, 0.1, 0.2, 0.25, 0.3, 0.4, 0.45, 0.5, 0.6, 0.65, 0.7, 0.75, 0.85, 0.9, 1]
                volume = arr[int(volume * 100)]
            # 调整音量
            await dlna.async_set_volume_level(volume)

    async def async_play_media(self, media_type, media_id, **kwargs):            
        dlna = self.dlna_device
        if dlna is not None:
            await dlna.async_set_transport_uri(media_id, "小米电视 - HomeAssistant")

    async def async_media_play(self):
        dlna = self.dlna_device
        if dlna is not None and dlna.transport_state in (
                TransportState.PAUSED_PLAYBACK,
                TransportState.PAUSED_RECORDING,
            ):
            await dlna.async_play()            
            self._state = STATE_PLAYING
        else:
            await self.keyevent('enter')

    async def async_media_pause(self):
        dlna = self.dlna_device
        if dlna is not None and dlna.transport_state in (
                TransportState.PLAYING,
                TransportState.TRANSITIONING,
            ):
            await dlna.async_pause()
            self._state = STATE_PAUSED
        else:
            await self.keyevent('enter')

    async def async_media_next_track(self):
        await self.keyevent('right')

    async def async_media_previous_track(self):
        await self.keyevent('left')

    # 发送事件
    def fire_event(self, cmd):
        self.hass.bus.async_fire("xiaomi_tv", { 'entity_id': self.entity_id, 'type': cmd })

    # 获取安装APP
    async def get_apps(self):
        # 获取本机APP列表
        res = await self.execute('getinstalledapp&count=999&changeIcon=1')
        if res is not None:
            AppInfo = res['data']['AppInfo']
            for app in AppInfo:
                self.apps.update({ app['AppName']: app['PackageName'] })
        # 绑定数据源
        _source_list = []
        for name in self.apps:
            _source_list.append(name)
        self._source_list = _source_list
        self.app_list = _source_list

    # 获取执行命令
    async def execute(self, cmd):
        return await self.http(f'controller?action={cmd}')

    # 执行按键命令
    async def keyevent(self, keycode):
        return await self.http(f'controller?action=keyevent&keycode={keycode}')

    # 获取电视信息
    async def getsysteminfo(self):
        res = await self.execute('getsysteminfo')
        if res is not None:
            data = res['data']
            #self._attributes['deviceid'] = data['deviceid']
            # 可以根据设备名称判断类型，电视、盒子 
            devicename = data['devicename']
            self._attr_media_title = devicename
            #self._attributes['devicename'] = devicename
            #self._attributes['ethmac'] = data['ethmac']
            #self._attributes['wifimac'] = data['wifimac']
            # ['hdmi1', 'hdmi2', 'hdmi3', 'gallery', 'aux', 'tv', 'vga', 'av', 'dtmb']
            if '电视' in devicename:
                self._sound_mode_list = ['hdmi1', 'hdmi2', 'hdmi3', 'gallery', 'aux', 'tv', 'vga', 'av', 'dtmb']
            return res

    # 获取执行命令
    async def http(self, url):
        try:
            if self.is_alive:
                request_timeout = aiohttp.ClientTimeout(total=1)
                async with aiohttp.ClientSession(timeout=request_timeout) as session:
                    async with session.get(f'http://{self.ip}:6095/{url}') as response:
                        data = json.loads(await response.text())
                        return data
        except Exception as ex:
            _LOGGER.debug(ex)
        return None

    # 截图方法
    async def capturescreen(self):
        # 截图
        params = self.with_opaque({'action': 'capturescreen', 'compressrate': 100})
        res = await self.http(f'controller?{urlencode(params)}')
        if res is not None:
            rdt = res['data']
            # print(rdt)
            # 获取图片
            token = rdt.get('token')
            params = self.with_opaque({'action': 'getResource', 'name': 'screenCapture'}, token)
            self._attr_media_image_url = f'http://{self.ip}:6095/request?{urlencode(params)}'
            self._attr_app_id = rdt.get('pkg')
            self._attr_app_name = rdt.get('label')

    def with_opaque(self, pms, token=None):
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

    # 创建DLNA设备
    async def create_dlna_device(self):
        requester = AiohttpRequester()
        factory = UpnpFactory(requester)
        url = f"http://{self.ip}:49152/description.xml"
        # print(url)
        device = await factory.async_create_device(url)

        def event_handler(**args):
            print(args)

        self.dlna_device = DmrDevice(device, event_handler)

        # 订阅事件通知
        # self.dlna_device.on_event = self._on_event
        # await self.dlna_device.async_subscribe_services(auto_resubscribe=True)

        # 获取音量
        # get RenderingControle-service
        service = device.service("urn:schemas-upnp-org:service:RenderingControl:1")
        # perform GetVolume action
        get_volume = service.action("GetVolume")
        result = await get_volume.async_call(InstanceID=0, Channel="Master")
        # print(result)
        self._volume_level = result['CurrentVolume'] / 100

    ''' 有时间再研究
    def _on_event(self, service, state_variables):
        if not state_variables:
            # Indicates a failure to resubscribe, check if device is still available
            self.check_available = True
        print(service, state_variables)
    '''