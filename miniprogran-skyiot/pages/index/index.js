const { data } = require("../../mixin/common.js")
const app = getApp()

// index.js
Page({
    data:{
        state: false,
        device: app.globalData.device_id,
        connectState:"应用启动...",
        toastVars:{
            textToast: false,
            hideTextToast: false,
            toastInfo:""
        },
        topTips: false,
        hide: false,
    },
    onLoad:function(){
        this.tipsOpen()
        app.globalData.lanunchCallback = this.topTipsCallback
    },

    onReady: function () {
        app.globalData.uploadCallback = this.messageCallBack
    },

    onShow: function () {
        this.setData({
            device: app.globalData.device_id,
        })
    },

    onHide: function () {

    },

    switchBtnClick:function(e){
        var flag = !e.currentTarget.dataset.checked
        this.setData({state:flag})

        // var query = wx.createSelectorQuery();
        // query.select('.switch_led').boundingClientRect();
        // query.exec(function(res){
        //     console.log(res[0])
        // })

        const topic = "device/"+app.globalData.device_id+"/control/led"
        const msg = {
            "state":flag?"on":"off"
        }

        console.log(topic, JSON.stringify(msg))
        app.mqttClientPush(topic, JSON.stringify(msg))

        this.setData({
            toastVars:{
                toastInfo:flag?"已打开":"已关闭"
            }
        })
        this.openTextToast()
    },

    messageCallBack:function(topic, message){
        console.log('received msg:' + message.toString());
    },

    topTipsCallback:function(msg, state){
        this.setData({
            connectState:msg
        })
        if(state){
            setTimeout(() => {
                this.tipsClose() 
            }, 1000);
        }else{
            this.tipsOpen()
        }
    },

    openTextToast() {
        this.setData({
          textToast: true,
        });
        setTimeout(() => {
          this.setData({
            hideTextToast: true,
          });
          setTimeout(() => {
            this.setData({
              textToast: false,
              hideTextToast: false,
            });
          }, 300);
        }, 3000);
      },

    tipsClose() {
        this.setData({
            hide: true,
        });
        setTimeout(() => {
            this.setData({
            topTips: false,
            hide: false,
            });
        }, 300);
    },
    tipsOpen() {
        this.setData({
            topTips: true,
        });
    },
})
