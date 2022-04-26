package com.example.att_network_test

import android.content.ContentValues.TAG
import android.content.Context
import android.net.wifi.WifiManager
import android.os.Bundle
import android.os.PowerManager
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.WindowManager
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.dandan.jsonhandleview.library.JsonViewLayout
import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.ktx.firestore
import com.google.firebase.ktx.Firebase
import com.ookla.speedtest.sdk.*
import com.ookla.speedtest.sdk.config.*
import com.ookla.speedtest.sdk.handler.MainThreadTestHandler
import com.ookla.speedtest.sdk.handler.TaskManagerController
import com.ookla.speedtest.sdk.model.LatencyResult
import com.ookla.speedtest.sdk.model.ThroughputStage
import com.ookla.speedtest.sdk.model.TransferResult
import com.ookla.speedtest.sdk.result.OoklaError

import kotlinx.android.synthetic.main.activity_test.*
import kotlinx.coroutines.*
import java.lang.Runnable

import java.lang.RuntimeException

/**
 * Contains the logic to execute the different tests available as part of the Speedtest SDK
 *
 * Look at this class for examples of how to use [TaskManager] to run tests as
 * well as how to pass in [TestHandler][com.ookla.speedtest.sdk.handler.TestHandler] to listen to progress updates and get the results
 */
class TestActivity : AppCompatActivity() {
    private val testConfigBgSpeed = "defaultTriggeredTest"
    private val testConfigBgScan = "defaultSignalScan"
    private val testConfigCITest = "5gnetworktest"

    private val db = Firebase.firestore

    enum class TestFunctionality(val title: String) {
        SingleTest("Start Single Test"),
        ShortTest("Start Short Test"),
        FetchStoredResult("Fetch Stored Test Result"),
    }

    private var wakeLock : PowerManager.WakeLock? = null
    private var wifiLock : WifiManager.WifiLock? = null
    private var taskManager: TaskManager? = null



    private var uploadSpeed: Double?= 0.0
    private var downloadSpeed: Double?= 0.0



    private var testFinished: Boolean = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_test)

        val powerManager =
            getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "SDK:SDKWakeLock")

        val wm = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        wifiLock = wm.createWifiLock(WifiManager.WIFI_MODE_FULL, "SDK:SDKWifiLock")

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        val inst = SpeedtestSDK.getInstance()
        val testFunctionality = intent.getSerializableExtra("testFunctionality") as TestFunctionality

        if(testFunctionality != TestFunctionality.FetchStoredResult) {
//            output.text = "Start fetching config ...\n"
        }

        when (testFunctionality) {
            TestFunctionality.SingleTest->{
                runShortTest(inst)
            }
            TestFunctionality.ShortTest -> {
                runShortTest(inst)
            }

            TestFunctionality.FetchStoredResult -> {
                runFetchStoredResult(inst)
            }

        }
    }

    private fun runFetchStoredResult(speedtestSDK: SpeedtestSDK) {
        val guid = MainActivity.lastTestGuid
        val logger = LoggingTestHandler(output, jsonView)

        if(guid == null) {
            logger.log("A test needs to be run first to fetch the stored result.")
            return
        }
        if (guid != null) {
            logger.log(guid)
        }
        logger.log("Fetching stored result for guid $guid...")
        speedtestSDK.fetchResult(guid, MainActivity.SPEEDTEST_SDK_RESULT_KEY) { result, error ->
            if(result != null) {
                logger.log("Got result")
                try {
                    jsonView.bindJson(result.toJson())

                } catch(exc: RuntimeException) {
                    logger.log("Failed to convert result to json: ${exc.localizedMessage}")
                }
            } else if(error != null) {
                logger.log("Failed to fetch result: ${error.message} (${error.type})")
            }
        }


    }

    private fun runSingleTest(speedtestSDK: SpeedtestSDK) {
        val config = Config.newConfig(testConfigCITest)
        config?.tasks = arrayListOf(Task.newThroughputTask(), Task.newServerTracerouteTask(), Task.newPacketlossTask())
        // test against a single server
        config?.serverIdForTesting = 6029
        val configHandler = object : ConfigHandlerBase() {
            override fun onConfigFetchFinished(validatedConfig: ValidatedConfig?) {
                if (testFinished) {
                    runFetchStoredResult(speedtestSDK)
//                    return;
                }

                val handlerWithStageProgression =
                    UiTestHandlerWithStageProgression(
                        output, jsonView
                    )
                val handler = MainThreadTestHandler(
                    handlerWithStageProgression
                )

                output.text = "Config retrieved over connection type ${validatedConfig?.connectionType.toString()}\n"
                taskManager = speedtestSDK.newTaskManager(handler, validatedConfig)
                taskManager?.start()
            }

            override fun onConfigFetchFailed(error: OoklaError) {
                output.append("Config fetch failed with ${error.message}\n")
                onBackPressed()
            }
        }

        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }


    private fun runShortTest(speedtestSDK: SpeedtestSDK) {
        val config = Config.newConfig(testConfigCITest)
        config?.transferTestDurationSeconds = 5
        val configHandler = object : ConfigHandlerBase() {
            override fun onConfigFetchFinished(validatedConfig: ValidatedConfig?) {
                if (testFinished) {
                    return;
                }
                val handlerWithStageProgression =
                    UiTestHandlerWithStageProgression(
                        output, jsonView
                    )
                val handler = MainThreadTestHandler(
                    handlerWithStageProgression
                )
                taskManager = speedtestSDK.newTaskManager(handler, validatedConfig)
                taskManager?.start()



            }

            override fun onConfigFetchFailed(error: OoklaError) {
                output.append("Config fetch failed with ${error.message}\n")
                onBackPressed()
            }
        }
        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }


    override fun onBackPressed() {
        testFinished = true;

        taskManager?.cancel()
        taskManager = null

        super.onBackPressed()
    }

    override fun onDestroy() {
        super.onDestroy()

        wifiLock?.isHeld?.let {
            if (it) {
                wifiLock?.release()
            }
        }
        wakeLock?.isHeld?.let {
            if (it) {
                wakeLock?.release()
            }
        }
    }


    inner class UiTestHandlerWithStageProgression (output: TextView, jsonView: JsonViewLayout) : LoggingTestHandler(output, jsonView) {
        override fun onLatencyFinished(taskController: TaskManagerController?, result: LatencyResult) {
            super.onLatencyFinished(taskController, result)
            taskManager?.startNextStage()
        }

        override fun onDownloadFinished(taskController: TaskManagerController?, result: TransferResult) {
            super.onDownloadFinished(taskController, result)
            taskManager?.startNextStage()
        }

        override fun onTestFailed(error: OoklaError, speedtestResult: SpeedtestResult?) {
            super.onTestFailed(error, speedtestResult)
            onBackPressed()
        }

        override fun onTestFinished(speedtestResult: SpeedtestResult) {
            super.onTestFinished(speedtestResult)
            val logger = LoggingTestHandler(output, jsonView)

            val resultObj = speedtestResult.resultObj
            MainActivity.lastTestGuid = resultObj.guid
            logger.log(resultObj.download?.speedKbps.toString())
            logger.log(resultObj.upload?.client?.speedKbps.toString())
            uploadSpeed = resultObj.upload?.client?.speedKbps?.toDouble()
            downloadSpeed = resultObj.download?.speedKbps?.toDouble()

            val data = hashMapOf(
                "upload" to uploadSpeed,
                "download" to downloadSpeed,
                "latitude" to MainActivity.latitude,
                "longitude" to MainActivity.longitude,
                "altitude" to MainActivity.altitude,
                "time_stamp" to FieldValue.serverTimestamp(),
                "zipcode" to ""
            )
            db.collection("data")
                .add(data)
                .addOnSuccessListener { documentReference ->
                    println( "DocumentSnapshot added with ID: ${documentReference.id}")
                }
                .addOnFailureListener { e ->
                    println("Error adding document")
                }
            db.collection("operations").document("newest")
                .set(data)
                .addOnSuccessListener { Log.d(TAG, "DocumentSnapshot successfully written!") }
                .addOnFailureListener { e -> Log.w(TAG, "Error writing document", e) }

            onBackPressed()


        }
    }

}
