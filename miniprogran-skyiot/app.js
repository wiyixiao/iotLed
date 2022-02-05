// app.js
const listeners = [];
App({
    globalData: {
        theme: 'light', // dark
        mode: '', // 模式(care：关怀模式)
        device_id:"skyiot_esp_001",
        mqttHost:"www.wiyixiao4.com/mqtt",
        mqttPort:443,
        mqttUser:"",
        mqttPasswd:"",
        mqttObj:null,
        mqttClient:null,
        uploadCallback:null,
        settingCallback:null,
      },
      data:{

      },
      changeGlobalData(data) {
        this.globalData = Object.assign({}, this.globalData, data);
        listeners.forEach((listener) => {
          listener(this.globalData);
        });
      },
      watchGlobalDataChanged(listener) {
        if (listeners.indexOf(listener) < 0) {
          listeners.push(listener);
        }
      },
      unWatchGlobalDataChanged(listener) {
        const index = listeners.indexOf(listener);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      },
      onThemeChange(resp) {
        this.changeGlobalData({
          theme: resp.theme,
        });
      },
      onLaunch() {
        // TODO: 检测适老化
        console.log("App launch")
        this.globalData.mqttObj = require("./libs/mqtt_3.min")
        this.mqttConfigRead() //读取本地配置
        // return
        this.mqttClientConnect()
        
      },
      
      mqttClientConnect:function(){
        if(this.globalData.mqttClient == null){
            const mqttOptions ={
              keepalive:30,
              clean:true,
              connectTimeout: 3000, // 超时时间
              reconnectPeriod:1000,
              clientId: 'wx_' + parseInt(Math.random() * 100 + 800, 10),
              port: this.globalData.mqttPort,  
              username: this.globalData.mqttUser,
              password: this.globalData.mqttPasswd,
            }

            this.globalData.mqttClient = this.globalData.mqttObj.connect('wxs://'+this.globalData.mqttHost,mqttOptions)

            //重新连接
            this.globalData.mqttClient.on('reconnect', (error) => {
                console.log('正在重连:', error)
                getApp().globalData.lanunchCallback("正在重连...", false)
            })

            //连接失败
            this.globalData.mqttClient.on('error', (error) => {
                console.log('连接失败:', error)
                getApp().globalData.lanunchCallback("连接服务器失败", false)
            })

            let that = this;
            this.globalData.mqttClient.on('connect', (e) => {
                console.log('成功连接服务器')
                console.log(this.globalData.mqttClient.connected)
                getApp().globalData.lanunchCallback("成功连接服务器", true)
                //订阅主题
                var topics = {'uploadMsg': {qos: 0}, 'settingMsg': {qos: 0}}
                this.globalData.mqttClient.subscribe(topics, function(err) {
                    if (!err) {
                        console.log("订阅成功")
                    }
                })
            })

            //设置接收回调
            this.globalData.mqttClient.on('message', this.mqttMessageCallback)
        }else if(this.globalData.mqttClient.connected == false){
          console.log("需要重连")
        }
      },

      mqttClientClose:function(){
        if(this.globalData.mqttClient != null){
            // this.globalData.mqttClient.unsubscribe(['uploadMsg', 'settingMsg'])
            this.globalData.mqttClient.end(true)
            this.globalData.mqttClient = null
        }
      },

      mqttClientReconnect:function(){
        if(this.globalData.mqttClient != null){
          this.globalData.mqttClient.reconnect()
      }
      },

      mqttMessageCallback:function(topic, message){
        if(topic == "uploadMsg"){
            if(this.globalData.uploadCallback != null){
                this.globalData.uploadCallback(topic, message)
            }
        }else if(topic = "settingMsg"){
            if(this.globalData.settingCallback != null){
                this.globalData.settingCallback(topic, message)
            }
        }
      },

      mqttClientPush:function(topic, msg){
        if(this.globalData.mqttClient != null){
            this.globalData.mqttClient.publish(topic, msg)
        }
      },

      mqttConfigSave:function(){
        wx.setStorageSync("keyid", this.globalData.device_id)
        wx.setStorageSync("keyhost", this.globalData.mqttHost)
        wx.setStorageSync('keyport', this.globalData.mqttPort)
        wx.setStorageSync('keyuser', this.globalData.mqttUser)
        wx.setStorageSync('keypasswd', this.globalData.mqttPasswd)

      },

      mqttConfigRead:function(){
        this.globalData.device_id = wx.getStorageSync("keyid")
        this.globalData.mqttHost = wx.getStorageSync("keyhost")
        this.globalData.mqttPort = wx.getStorageSync("keyport")
        this.globalData.mqttUser = wx.getStorageSync("keyuser")
        this.globalData.mqttPasswd = wx.getStorageSync("keypasswd")

        if(this.globalData.device_id == ""){
          this.globalData.device_id = "skyiot_esp_001"
        }
        if(this.globalData.mqttHost == ""){
          this.globalData.mqttHost = "www.wiyixiao4.com/mqtt"
        }
        if(this.globalData.mqttPort == ""){
          this.globalData.mqttPort = "443"
        }

        console.log(
          this.globalData.device_id,
          this.globalData.mqttHost,
          this.globalData.mqttPort,
          this.globalData.mqttUser,
          this.globalData.mqttPasswd
        )
      }
})
