package com.example.att_network_test
import android.app.Application
import com.ookla.speedtest.sdk.SimpleLogHandler
import com.ookla.speedtest.sdk.SpeedtestSDK

class SampleSDKApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        val inst = SpeedtestSDK.initSDK(this, MainActivity.SPEEDTEST_SDK_API_KEY)
        inst.setLogHandler(SimpleLogHandler())
    }
}