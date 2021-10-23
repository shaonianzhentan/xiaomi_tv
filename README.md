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

发送按键
```yaml
service: remote.send_command
data:
  command: left
```

## ADB服务

打开ADB（注意：必须先打开`开发者模式`）
```yaml
service: remote.send_command
data:
  command: adb
```
腾讯视频搜索
```yaml
service: xiaomi_tv.adb_command
data:
  command: am start -a com.tencent.qqlivetv.open -d "tenvideo2://?action=9&search_key=扫黑风暴"
  entity_id: media_player.xiao_mi_dian_shi
```
腾讯视频播放
```yaml
service: xiaomi_tv.adb_command
data:
  command: am start -a com.tencent.qqlivetv.open -d "tenvideo2://?action=7&cover_id=mzc00200lxzhhqz"
  entity_id: media_player.xiao_mi_dian_shi
```
酷瞄搜索
```yaml
service: xiaomi_tv.adb_command
data:
  command: am start -a android.intent.action.VIEW -d "ykott://tv/search?url=tv/v3/search?from_app=cn.cibntv.ott"
  entity_id: media_player.xiao_mi_dian_shi
```
酷瞄视频播放
```yaml
service: xiaomi_tv.adb_command
data:
  command: am start -a android.intent.action.VIEW -d "ykott://tv/detail?url=tv/v3/show/detail?id=175957&fullscreen=true&fullback=true&from=cn.cibntv.ott"
  entity_id: media_player.xiao_mi_dian_shi
```

## 更新日志

### v1.2
- 集成ADB服务
- 初始读取当前电视音量
- [ ] 视频搜索
- [ ] 视频播放

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