
// pages/wifiConfig/index.js
const sliderWidth = 96; // 需要设置slider的宽度，用于计算中间位置
const app = getApp()

Page({
    mixins: [require('../../mixin/common')],
    /**
     * 页面的初始数据
     */
    data: {
        device: app.globalData.device_id,
        settingMsg:"",
        udp:null,
        ap_ip:"192.168.4.1",
        ap_port:8888,
        wifi_ssid:"MERCURY_CC7C",
        wifi_passwd:"",
        tabs: ['网络设置', '参数设置','服务器设置'],
        activeIndex: 1,
        sliderOffset: 0,
        sliderLeft: 0,
        toastVars:{
          toast: false,
          hideToast: false,
          warnToast: false,
          hideWarnToast: false,
          toastInfo:"已完成"
        },
        mqtt_clientid:app.globalData.device_id,
        mqtt_host:app.globalData.mqttHost,
        mqtt_port:app.globalData.mqttPort,
        mqtt_user:app.globalData.mqttUser,
        mqtt_passwd:app.globalData.mqttPasswd
    },

    /**
     * 生命周期函数--监听页面加载
     */
    onLoad: function () {
        const that = this;
        this.data.udp = wx.createUDPSocket()
        this.data.udp.bind()
        this.data.udp.onMessage(this.onUdpMessage)
        wx.getSystemInfo({
          success(res) {
            that.setData({
              sliderLeft: (res.windowWidth / that.data.tabs.length - sliderWidth) / 2,
              sliderOffset: res.windowWidth / that.data.tabs.length * that.data.activeIndex,
            });
          },
        });
    },

    /**
     * 生命周期函数--监听页面初次渲染完成
     */
    onReady: function () {
      app.globalData.settingCallback = this.messageCallBack
    },

    /**
     * 生命周期函数--监听页面显示
     */
    onShow: function () {
      
    },

    /**
     * 生命周期函数--监听页面隐藏
     */
    onHide: function () {
    },

    /**
     * 生命周期函数--监听页面卸载
     */
    onUnload: function () {
      
    },

    /**
     * 页面相关事件处理函数--监听用户下拉动作
     */
    onPullDownRefresh: function () {

    },

    /**
     * 页面上拉触底事件的处理函数
     */
    onReachBottom: function () {

    },

    /**
     * 用户点击右上角分享
     */
    onShareAppMessage: function () {

    },

    onUdpMessage:function(res){
      if (res.remoteInfo.size > 0) {
        console.log('onUdpMessage() 接收数据 ' + res.remoteInfo.size + ' 字节：' + JSON.stringify(res, null, '\t'))
      }
    },

    tabClick(e) {
      this.setData({
        sliderOffset: e.currentTarget.offsetLeft,
        activeIndex: e.currentTarget.id,
      });

    },

    messageCallBack:function(topic, message){
      console.log('received msg:' + message.toString());
      if(topic == "settingMsg"){
        this.setData({
          settingMsg:message.toString()
        })
      }
  },

    apIpInput:function(e){
      this.setData({
        ap_ip:e.detail.value
      })
    },

    apPortInput:function(e){
      this.setData({
        ap_port:e.detail.value
      })
    },

    wifiSSIDInput:function(e){
      this.setData({
        wifi_ssid:e.detail.value
      })
    },

    wifiPasswdInput:function(e){
      this.setData({
        wifi_passwd:e.detail.value
      })
    },

    mqttClientIdInput:function(e){
      this.setData({
        mqtt_clientid:e.detail.value
      })
    },

    mqttHostInput:function(e){
      this.setData({
        mqtt_host:e.detail.value
      })
    },

    mqttPortInput:function(e){
      this.setData({
        mqtt_port:e.detail.value
      })
    },

    mqttUserInput:function(e){
      this.setData({
        mqtt_user:e.detail.value
      })
    },

    mqttPasswdInput:function(e){
      this.setData({
        mqtt_passwd:e.detail.value
      })
    },

    wifiConfigSubmit:function(e){
      console.log(this.data.ap_ip, this.data.ap_port, this.data.wifi_ssid, this.data.wifi_passwd)

      var info = ""
      var isok = true
      if(this.data.wifi_passwd == ""){
        info="密码不能为空"
        isok = false
      }else if(this.data.wifi_passwd.length < 8){
        info="密码长度小于8"
        isok = false
      }

      this.setData({
        toastVars:{
          toastInfo:info
        }
      })

      if(isok == false){
        this.openWarnToast()
      }else{
        //udp发送数据
        this.data.udp.send({
          address:this.data.ap_ip,
          port:this.data.ap_port,
          message:this.data.wifi_ssid.concat(",",this.data.wifi_passwd) //使用逗号拼接
        })
        this.setData({
          toastVars:{
            toastInfo:"已发送"
          }
        })
        this.openToast()
      }

    },

    mqttConfigSubmit:function(e){
      console.log(this.mqtt_clientid, this.data.mqtt_host, this.data.mqtt_port, this.data.mqtt_user, this.data.mqtt_passwd)

      app.globalData.device_id = this.data.mqtt_clientid
      app.globalData.mqttHost = this.data.mqtt_host
      app.globalData.mqttPort = this.data.mqtt_port
      app.globalData.mqttUser = this.data.mqtt_user
      app.globalData.mqttPasswd = this.data.mqtt_passwd

      app.mqttConfigSave() //保存服务器配置

      this.setData({
        toastVars:{
          toastInfo:"保存成功"
        }
      })
      this.openToast()
      app.mqttClientClose() //关闭连接
      setTimeout(() => {
        app.mqttClientConnect() //重新连接
      }, 1000);

    },

    readConfig:function(){
      const topic = "device/"+app.globalData.device_id+"/setting/r"
      const msg = {}
      console.log(topic, JSON.stringify(msg))
      app.mqttClientPush(topic, JSON.stringify(msg))
    },

    writeConfig:function(){
      const topic = "device/"+app.globalData.device_id+"/setting/w"
      const msg = this.data.settingMsg
      if(msg == ""){
        this.setData({
          toastVars:{
            toastInfo:"参数为空"
          }
        })
        this.openWarnToast()
        return
      }
      console.log(topic)
      app.mqttClientPush(topic, msg)
    },

    openToast() {
      this.setData({
        toast: true,
      });
      setTimeout(() => {
        this.setData({
          hideToast: true,
        });
        setTimeout(() => {
          this.setData({
            toast: false,
            hideToast: false,
          });
        }, 300);
      }, 3000);
    },

    openWarnToast() {
      this.setData({
        warnToast: true,
      });
      setTimeout(() => {
        this.setData({
          hidewarnToast: true,
        });
        setTimeout(() => {
          this.setData({
            warnToast: false,
            hidewarnToast: false,
          });
        }, 300);
      }, 3000);
    },
    
})