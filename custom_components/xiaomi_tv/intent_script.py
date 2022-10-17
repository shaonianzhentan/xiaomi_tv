import asyncio
from homeassistant.helpers import intent
import homeassistant.helpers.config_validation as cv
import re

def async_register(hass):
  arr = []
  states = hass.states.async_all()
  for state in states:
    domain = state.domain
    platform = state.attributes.get('platform')
    friendly_name = state.attributes.get('friendly_name')
    if state.domain == 'media_player' and platform == 'xiaomi':
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
            
            hass.async_create_task(hass.services.async_call(domain, 'play_media', {
              'entity_id': state.entity_id,
              'media_content_id': f'xiaomi://tv/search?kv={channel}',
              'media_content_type': 'video'
            }))
            
            response = intent_obj.create_response()
            response.async_set_speech(f"正在{name}上播放{channel}")
            return response