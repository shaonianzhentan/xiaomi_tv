from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_COMMAND
)
from .const import DOMAIN, SERVICE_ADB_COMMAND
from .utils import check_port

class MediaADB():

    def __init__(self, ip, media_player):
        self.ip = ip
        self.media_player = media_player
        self.adb = None
    
    async def async_update(self):
        if check_port(self.ip, 5555) == False:
            return
        try:
            if self.adb is not None and self.adb._available == True:
                return
            from adb_shell.auth.keygen import keygen
            from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
            from adb_shell.auth.sign_pythonrsa import PythonRSASigner
            hass = self.media_player.hass
            # Load the public and private keys
            adbkey = hass.config.path(STORAGE_DIR, "androidtv_adbkey")
            if not os.path.isfile(adbkey):
                keygen(adbkey)
            with open(adbkey) as f:
                priv = f.read()
            with open(adbkey + '.pub') as f:
                pub = f.read()
            signer = PythonRSASigner(pub, priv)
            # Connect
            device1 = AdbDeviceTcp(self.ip, 5555, default_transport_timeout_s=9.)
            device1.connect(rsa_keys=[signer], auth_timeout_s=0.1)
            self.adb = device1
            # 读取音量            
            volume_music_speaker = self.adb.shell('settings get system volume_music_speaker')
            self.media_player._volume_level = round(int(volume_music_speaker) / 15, 1)

            if hass.services.has_service(DOMAIN, SERVICE_ADB_COMMAND) == False:
                hass.services.async_register(DOMAIN, SERVICE_ADB_COMMAND, self.service_adb_command)
        except Exception as ex:
            self.adb = None
            print(ex)

    async def service_adb_command(self, service):
        cmd = service.data[ATTR_COMMAND]
        entity_id = service.data[ATTR_ENTITY_ID]
        if entity_id == self.media_player.entity_id:
            try:
                res = self.adb.shell(cmd)
                print(res)
            except Exception as ex:
                self.adb = None

    async def async_turn_off(self):
        self.adb = None