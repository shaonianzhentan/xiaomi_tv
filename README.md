# 小米电视

视频介绍：https://www.bilibili.com/read/cv12067446

[![hacs_badge](https://img.shields.io/badge/Home-Assistant-%23049cdb)](https://www.home-assistant.io/)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)


![visit](https://visitor-badge.glitch.me/badge?page_id=shaonianzhentan.xiaomi_tv&left_text=visit)
![forks](https://img.shields.io/github/forks/shaonianzhentan/xiaomi_tv)
![stars](https://img.shields.io/github/stars/shaonianzhentan/xiaomi_tv)


## 使用方式

安装完成重启HA，刷新一下页面，在集成里搜索`小米电视`即可

[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=xiaomi_tv)

HomeKit遥控器

[![导入蓝图](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fshaonianzhentan%2Fxiaomi_tv%2Fblob%2Fmain%2Fblueprints%2Fhomekit_tv_remote.yaml)

开机/关闭电视事件

[![导入蓝图](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fshaonianzhentan%2Fxiaomi_tv%2Fblob%2Fmain%2Fblueprints%2Fxiaomi_tv.yaml)


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
酷喵搜索
```yaml
service: xiaomi_tv.adb_command
data:
  command: am start -a android.intent.action.VIEW -d "ykott://tv/search?url=tv/v3/search?from_app=cn.cibntv.ott"
  entity_id: media_player.xiao_mi_dian_shi
```
酷喵视频播放
```yaml
service: xiaomi_tv.adb_command
data:
  command: am start -a android.intent.action.VIEW -d "ykott://tv/detail?url=tv/v3/show/detail?id=175957&fullscreen=true&fullback=true&from=cn.cibntv.ott"
  entity_id: media_player.xiao_mi_dian_shi
```

## 更新日志

### v1.4
- 内置在线直播源

### v1.3
- 支持电视调节音量
- 支持自定义直播源

### v1.2
- 集成ADB服务
- 初始读取当前电视音量
- 视频搜索
- 视频播放
- 支持集成安装
- 支持蓝图安装

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


#### 关注我的微信订阅号，了解更多HomeAssistant相关知识
<img src="https://github.com/shaonianzhentan/ha-docs/raw/master/docs/img/wechat-channel.png" align="left" height="160" alt="HomeAssistant家庭助理" title="HomeAssistant家庭助理"> 