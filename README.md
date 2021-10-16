# xiaomi_tv

小米电视

https://www.bilibili.com/read/cv12067446

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

> 功能命令（需要配置脚本）
- 小米电视历史记录：`xiaomi_history`
- 小米电视搜索：`xiaomi_search`
- 奇异果搜索：`iqiyi_search`
- 酷喵搜索：`youku_search`
- 腾讯视频搜索：`qqtv_search`

## 更新日志

### v1.1
- 集成DLNA服务
- 显示电视预览图
- 显示设备名称
- 显示当前打开APP
- 删除没用的参数
- 修复打开应用有时不成功的问题
- 修复无法打开ADB操作的命令
### v1.0
- 基本功能完成

## 如果这个项目对你有帮助，请我喝杯<del><small>咖啡</small></del><b>奶茶</b>吧😘
|支付宝|微信|
|---|---|
<img src="https://github.com/shaonianzhentan/ha-docs/raw/master/docs/img/alipay.png" align="left" height="160" width="160" alt="支付宝" title="支付宝">  |  <img src="https://github.com/shaonianzhentan/ha-docs/raw/master/docs/img/wechat.png" align="left" height="160" width="160" alt="微信支付" title="微信">