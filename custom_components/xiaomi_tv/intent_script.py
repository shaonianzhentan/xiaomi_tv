import asyncio
from homeassistant.helpers import intent
import homeassistant.helpers.config_validation as cv
import re

def async_register(hass):
  arr = []
  states = hass.states.async_all()
  for state in states:
    platform = state.attributes.get('platform')
    if state.domain == 'media_player' and platform == 'xiaomi':
      friendly_name = state.attributes.get('friendly_name')
      arr.append(friendly_name)

  length = len(arr)
  if length > 0:
    intent.async_register(hass, XiaomiTVIntent())
    hass.components.conversation.async_register(
          "XiaomiTVIntent",
          ["[在](" + "|".join(arr) + ")[上]播放{channel}"],
      )

class XiaomiTVIntent(intent.IntentHandler):

  intent_type = "XiaomiTVIntent"

  slot_schema = {
    'channel': cv.string
  }

  @asyncio.coroutine
  async def async_handle(self, intent_obj):
      hass = intent_obj.hass
      #print(intent_obj.slots)
      #print(intent_obj.text_input)
      channel = intent_obj.slots['channel']['value']

      matchObj = re.match(r'(在)?(.*)(上)?播放(.*)', intent_obj.text_input)
      if matchObj is not None:
        name = matchObj.group(2).strip('上')
        # print(name)
        # 名称匹配
        states = hass.states.async_all()
        for state in states:
          domain = state.domain
          platform = state.attributes.get('platform')
          friendly_name = state.attributes.get('friendly_name')
          if state.domain == 'media_player' and platform == 'xiaomi' and friendly_name == name:
            # CCTV转换
            if channel == '中央一台' or channel == '中央1台':
              channel = 'cctv-1'
            elif channel == '中央二台' or channel == '中央2台':
              channel = 'cctv-2'
            elif channel == '中央三台' or channel == '中央3台':
              channel = 'cctv-3'
            elif channel == '中央四台' or channel == '中央4台':
              channel = 'cctv-4'
            elif channel == '中央五台' or channel == '中央5台':
              channel = 'cctv-5'
            elif channel == '中央六台' or channel == '中央6台':
              channel = 'cctv-6'
            elif channel == '中央七台' or channel == '中央7台':
              channel = 'cctv-7'
            elif channel == '中央八台' or channel == '中央8台':
              channel = 'cctv-8'
            elif channel == '中央九台' or channel == '中央9台':
              channel = 'cctv-9'
            elif channel == '中央十台' or channel == '中央10台':
              channel = 'cctv-10'
            elif channel == '中央十一台' or channel == '中央11台':
              channel = 'cctv-11'
            elif channel == '中央十二台' or channel == '中央12台':
              channel = 'cctv-12'
            elif channel == '中央十三台' or channel == '中央13台':
              channel = 'cctv-13'
            elif channel == '中央十五台' or channel == '中央15台':
              channel = 'cctv-15'
            elif channel == '中央十七台' or channel == '中央17台':
              channel = 'cctv-17'

            # 调用小米电视直播服务
            hass.async_create_task(hass.services.async_call(domain, 'play_media', {
              'entity_id': state.entity_id,
              'media_content_id': f'xiaomi://tv/search?kv={channel}',
              'media_content_type': 'video'
            }))
            
            response = intent_obj.create_response()
            response.async_set_speech(f"正在{name}上播放{channel}")
            return response