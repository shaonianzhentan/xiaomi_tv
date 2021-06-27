# xiaomi_tv

小米电视

> HomeAssistant配置
```yaml
# 电视
media_player:
  - platform: xiaomi_tv
    host: 192.168.0.105

# 遥控器
remote:
  - platform: xiaomi_tv
    host: 192.168.0.105

# 日志
logger:
  default: info
  logs:
    custom_components.xiaomi_tv: debug
```

> 自定义配置`customize.yaml`
```yaml
# 控制音量
media_player.dian_shi:
  dlna: media_player.a_r_c_acadegc_3ca
```

> 开机事件自动化监听(触发条件)
```yaml
platform: event
event_type: xiaomi_tv
event_data:  
  type: 'on'
  entity_id: '电视实体，用来区分多个电视，只有一个可以去掉此项'
```

> 遥控器按键命令
- 关机：`power`
- 上：`up`
- 下：`down`
- 左：`left`
- 右: `right`
- 首页：`home`
- 音量加：`volumeup`
- 音量减：`volumedown`
- 菜单：`menu`
- 确定：`enter`
- 返回：`back`

> 功能命令
- 清除运行程序：`clear`