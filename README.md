# xiaomi_tv

在HA里使用的小盒精灵电视控制，

小盒精灵电视应用：http://www.dangbei.com/app/tv/2020/0222/7414.html
APP项目地址：https://gitee.com/mirrors/TVRemoteIME

> HomeAssistant配置
```yaml
# 配置
media_player:
  - platform: xiaomi_tv
    host: 192.168.0.105

# 日志
logger:
  default: info
  logs:
    custom_components.xiaomi_tv: debug
```

> 开机事件自动化监听(触发条件)
```yaml
platform: event
event_type: xiaomi_tv
event_data:
  ip: 192.168.0.105
  type: 'on'
```
