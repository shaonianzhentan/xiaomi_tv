customElements.whenDefined("hui-view").then(() => {
    customElements.define('tv-remote-card', class extends HTMLElement {
        constructor() {
            super();
            this.attachShadow({ mode: 'open' });
        }

        set hass(hass) {
            this._hass = hass;
            this._entity = this.config.entity;
            if (['not_home', 'off'].includes(this._hass.states[this._entity].state)) {
                if (this.hacard && !this.hacard.classList.contains('not_home')) {
                    this.hacard.classList.add('not_home')
                }
            }
        }

        // 自定义默认配置
        static getStubConfig() {
            const defaultEntity = 'media_player.xiao_mi_dian_shi'
            const defaultRemote = 'remote.xiao_mi_dian_shi'
            return {
                vibrate: true,
                entity: defaultEntity,
                circle: {
                    ok: {
                        service: 'remote.send_command',
                        data: {
                            command: 'enter',
                            entity_id: defaultRemote
                        }
                    },
                    up: {
                        service: 'remote.send_command',
                        data: {
                            command: 'up',
                            entity_id: defaultRemote
                        }
                    },
                    down: {
                        service: 'remote.send_command',
                        data: {
                            command: 'down',
                            entity_id: defaultRemote
                        }
                    }, left: {
                        service: 'remote.send_command',
                        data: {
                            command: 'left',
                            entity_id: defaultRemote
                        }
                    }, right: {
                        service: 'remote.send_command',
                        data: {
                            command: 'right',
                            entity_id: defaultRemote
                        }
                    }
                },
                right_buttons: [
                    {
                        icon: 'mdi:power',
                        service: 'remote.send_command',
                        data: {
                            command: 'power',
                            entity_id: defaultRemote
                        },
                    },
                    {
                        icon: 'mdi:keyboard-return',
                        service: 'remote.send_command',
                        data: {
                            command: 'back',
                            entity_id: defaultRemote
                        }
                    },
                    {
                        icon: 'mdi:home',
                        service: 'remote.send_command',
                        data: {
                            command: 'home',
                            entity_id: defaultRemote
                        }
                    },
                    {
                        icon: 'mdi:menu',
                        service: 'remote.send_command',
                        data: {
                            command: 'menu',
                            entity_id: defaultRemote
                        }
                    },
                    {
                        icon: 'mdi:volume-minus',
                        service: 'remote.send_command',
                        data: {
                            command: 'volumedown',
                            entity_id: defaultRemote
                        }
                    },
                    {
                        icon: 'mdi:volume-plus',
                        service: 'remote.send_command',
                        data: {
                            command: 'volumeup',
                            entity_id: defaultRemote
                        }
                    },
                ],
                bottom_buttons: [
                    {
                        icon: 'mdi:android',
                        service: 'remote.send_command',
                        data: {
                            command: 'adb',
                            entity_id: defaultRemote
                        },
                    },
                    {
                        icon: 'mdi:movie-open-settings',
                        service: 'media_player.select_source',
                        data: {
                            source: '银河奇异果',
                            entity_id: defaultEntity
                        },
                    },
                    {
                        icon: 'mdi:cat',
                        service: 'media_player.select_source',
                        data: {
                            source: 'CIBN酷喵',
                            entity_id: defaultEntity
                        },
                    },
                    {
                        icon: 'mdi:cloud',
                        service: 'media_player.select_source',
                        data: {
                            source: '云视听极光',
                            entity_id: defaultEntity
                        },
                    },
                    {
                        icon: 'mdi:kodi',
                        service: 'media_player.select_source',
                        data: {
                            source: 'Kodi',
                            entity_id: defaultEntity
                        },
                    },
                ]
            }
        }

        setConfig(config) {
            if (!config.entity) {
                throw new Error('你需要定义一个实体');
            }
            this.config = config;

            const root = this.shadowRoot;
            if (root.lastChild) root.removeChild(root.lastChild);
            const style = document.createElement('style');
            style.textContent = this._cssData();
            root.appendChild(style);
            this.hacard = document.createElement('ha-card');
            this.hacard.className = 'f-ha-card';
            this.hacard.innerHTML = this._htmlData();
            root.appendChild(this.hacard);
            const $ = this.hacard.querySelector.bind(this.hacard);
            // 环形按钮
            Object.keys(this.config.circle).forEach(key => {
                const ele = $(`#l${key}`)
                let value = this.config.circle[key]
                ele.onclick = () => {
                    if (typeof value === 'string') {
                        this.selectMode(value)
                    } else {
                        this.selectMode(value.service, value.data)
                    }
                }
            })
            // 左侧按钮
            if (this.config.right_buttons) {
                this.config.right_buttons.forEach(function (button) {
                    let buttonBox = document.createElement('paper-button');
                    buttonBox.innerHTML = `
                        <div class="lbicon">
                            <ha-icon class="ha-icon" data-state="on" icon="`+ button.icon + `"></ha-icon>
                        </div>
                    `;
                    buttonBox.addEventListener('click', (e) => {
                        if ('entity' in button) {
                            this.selectMode(button.entity)
                        } else {
                            this.selectMode(button.service, button.data)
                        }
                    }, false);
                    this.hacard.querySelector("#right_buttons").appendChild(buttonBox)
                }, this)
            }
            // 底部按钮
            if (this.config.bottom_buttons) {
                this.config.bottom_buttons.forEach(function (button) {
                    let buttonBox = document.createElement('paper-button');
                    buttonBox.innerHTML = `
                        <div class="lbicon">
                            <ha-icon class="ha-icon" data-state="on" icon="`+ button.icon + `"></ha-icon>
                        </div>
                    `;
                    buttonBox.addEventListener('click', (e) => {
                        if ('entity' in button) {
                            this.selectMode(button.entity)
                        } else {
                            this.selectMode(button.service, button.data)
                        }
                    }, false);
                    this.hacard.querySelector("#bottom_buttons").appendChild(buttonBox)
                }, this)
            }
        }

        selectMode(service_name, data = {}) {
            var arr = service_name.split('.');
            var domain = arr[0];
            var service = arr[1];
            this._hass.callService(domain, service, data)
            // 震动
            if (this.config.vibrate && navigator.vibrate) {
                navigator.vibrate(50)
            }
        }

        _htmlData() {
            var html = `       
        <div id="remote" class="remote_f">
            <div class="box">
                <div class="scale">
                    <div class="button-group">
                        <div class="outter-circle">
                            <div class="inner-parts up">
                                <div class="iconbox">
                                    <div class="ficon"></div>
                                </div>
                                <div id="lup" class="tap up"></div>
                            </div>
                            <div class="inner-parts right">
                                <div class="iconbox">
                                    <div class="ficon"></div>
                                </div>
                                <div id="lright" class="tap right"></div>
                            </div>
                            <div class="inner-parts left">
                                <div class="iconbox">
                                    <div class="ficon"></div>
                                </div>
                                <div id="lleft" class="tap left"></div>
                            </div>
                            <div class="inner-parts down">
                                <div class="iconbox">
                                    <div class="ficon"></div>
                                </div>
                                <div id="ldown" class="tap down"></div>
                            </div>
                            <div id="lok" class="inner-circle ok">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="boxb">
                <div id="right_buttons">
                </div>
            </div>
        </div>
        <div id="bottom_buttons"></div>
    `
            return html;
        }
        _cssData() {
            var css = `
        #remote{
            display:flex;
            flex-wrap: wrap;
            justify-content: center;
        }
        .f-ha-card{
            padding: 1pc;
            background: var(--paper-card-background-color);
            --box-shadow:2px 2px 5px rgba(0, 0, 0, 0.3);
            --button-shadow-color:#00bcd4;
            --state-color-off: gray;
        }
        .box {
            padding: 5px;
            overflow: hidden;
            flex:1.25;
            display: flex;
            align-items: center;
            min-width: 165px;
        }
        .boxb {
            flex:1;
            min-width: 145px;
        }
        .scale {
            width: 100%;
            padding-bottom: 100%;
            height: 0;
            position: relative;
        }
      .button-group {
        width: 100%;
        height: 100%;
        position: absolute;
      }
      .outter-circle {
        position: relative;
        width: 100%;
        height: 100%;
        transform-origin: center;
        transform: rotate(45deg);
      }
      .inner-parts {
        float: left;
        width: 49.5%;
        height:49.5%;
        background-color: var(--card-color-off);
        opacity: 7.5;
        box-sizing: border-box;
        border: 1px #ffffff17 solid;
        box-shadow: var(--box-shadow) ;
      }
      .up{
        margin:0 0.5% 0.5% 0;
        border-top-left-radius: 100%;
      }
      .right{
        margin:0 0 0.5% 0.5%;
        border-top-right-radius: 100%;
      }
      .left{
        margin:0.5% 0.5% 0 0 ;
        border-bottom-left-radius: 100%;
      }
      .down{
        margin:0.5% 0 0 0.5% ;
        border-bottom-right-radius: 100%;
      }
      .inner-circle {
        position: absolute;
        margin-top: 28%;
        margin-left: 28%;
        width: 44%;
        height:44%;
        border-radius: 100%;
        background-image: var(--card-color-off);
        background: var(--paper-card-background-color);
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.3) ;
        box-sizing: border-box;
        border: 1px #ffffff17 solid;
      }
      .inner-circle:active{
            background-image: var(--card-color-off);
            box-shadow: 0px 0px 5px var(--accent-color) inset;
        }
        .rotate {
            display: inline-block;
            transform: rotate(-45deg);
            width: 100%;
            height:100%;
            line-height: 90px;
        }
        .iconbox{
            position: relative;
            display: block;
            width: 5%;
            color: #FFFFFF;
            height: 5%;
            margin: 47%;
        }
        .ficon{
            width: 100%;
            color: #FFFFFF;
            height: 100%;
            vertical-align: middle;
            border-radius: 50%;
            background-size: cover;
            background-color: var(--accent-color);
            text-align: center;
            box-shadow: 1px 1px 6px rgba(0, 0, 0, 0.6);
        } 
        .tap{
            position: relative;
            width: 100%;
            height: 100%;
            top: -100%;
            left: 0;
        }
        .tap:active{
            box-shadow: 2px 2px 5px var(--accent-color);
        }
        #right_buttons,
        #bottom_buttons {
            display: flex;
            flex-wrap: wrap;
            align-content: center;
            min-height: 100%;
            justify-content: center;
        }
        paper-button {
            text-align: center;
            padding: 5px;
            border-radius: 50%;
            margin: 10px;
            color: var(--accent-color);
            box-shadow: var(--box-shadow);
            box-sizing: border-box;
            border: 1px #ffffff17 solid;
        }
        paper-button:active{
            box-shadow: 0 0 5px var(--accent-color);
        }
        .lbicon {
            cursor: pointer;
            position: relative;
            display: inline-block;
            width: 40px;
            color: var(--accent-color);
            height: 40px;
            text-align: center;
            background-size: cover;
            line-height: 40px;
            vertical-align: middle;
            border-radius: 50%;
        }
        .not_home .lbicon {
            color: var(--state-color-off);
        }
        .not_home .ficon {
            background-color: var(--state-color-off);
        }
        `
            return css;
        }
        getCardSize() {
            return 1;
        }
    });
    // 添加预览
    window.customCards = window.customCards || [];
    window.customCards.push({
        type: "tv-remote-card",
        name: "电视遥控器",
        preview: true,
        description: "电视遥控器卡片"
    });
})