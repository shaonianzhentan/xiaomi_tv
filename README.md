# xiaomi_tv

在HA里使用的小米电视（基于官方版本修改）

> 新增功能
- 支持更换数据源
- 支持选择打开APP

> 开机事件自动化监听(触发条件)
```yaml
platform: event
event_type: xiaomi_tv
event_data:
  ip: 192.168.0.105
  type: 'on'
```