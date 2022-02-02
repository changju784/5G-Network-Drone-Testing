package com.example.att_network_test

import android.content.Context
import android.net.wifi.WifiManager
import android.os.Bundle
import android.os.PowerManager
import android.util.Log
import android.view.WindowManager
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.dandan.jsonhandleview.library.JsonViewLayout
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
        ServerSelection("Run Server Selection"),
        SingleTest("Start Single Test"),
        SingleTestWithAutoServerSelection("Start Test With Auto Server Selection"),
        ShortTest("Start Short Test"),
        BackgroundCaptureDeviceTask("Start Background Scan"),
        BackgroundThroughputTask("Start Background Speedtest"),
        Traceroute("Run Multiple Traceroutes"),
        UploadAndTraceroute("Run Upload and Traceroute Test"),
        TestWithSupplementalData("Test With Supplemental Data"),
        FetchStoredResult("Fetch Stored Test Result"),
        DeleteSavedConfigs("Remove Saved Config"),
        ReinitSDK("Reinitialize SDK")
    }

    private var wakeLock : PowerManager.WakeLock? = null
    private var wifiLock : WifiManager.WifiLock? = null
    private var taskManager: TaskManager? = null



    private var uploadSpeed: Double?= 0.0
    private var downloadSpeed: Double?= 0.0
    private var latitude: Double?= 0.0
    private var longitude: Double? = 0.0


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
            TestFunctionality.SingleTest -> {
                runSingleTest(inst)

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
        logger.log("Fetching stored result for guid $guid...")
        speedtestSDK.fetchResult(guid, MainActivity.SPEEDTEST_SDK_RESULT_KEY) { result, error ->
            if(result != null) {
                logger.log("Got result")
                try {
                    jsonView.bindJson(result.toJson())
                    uploadSpeed = result.uploadMbps
                    downloadSpeed = result.downloadMbps
                    latitude = ((result.endLatitude + result.startLatitude) /2).toDouble()
                    longitude = ((result.endLongitude + result.startLongitude) /2).toDouble()

                    val user = hashMapOf(
                        "upload" to uploadSpeed,
                        "download" to downloadSpeed,
                        "latitude" to latitude,
                        "longitude" to longitude
                    )
                    db.collection("users")
                        .add(user)
                        .addOnSuccessListener { documentReference ->
                            println( "DocumentSnapshot added with ID: ${documentReference.id}")
                        }
                        .addOnFailureListener { e ->
                            println("Error adding document")
                        }


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
                    return;
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
//                taskManager?.
            }

            override fun onConfigFetchFailed(error: OoklaError) {
                output.append("Config fetch failed with ${error.message}\n")
            }
        }

        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }

    private fun runSingleTestWithAutoServerSelection(speedtestSDK: SpeedtestSDK) {
        val config = Config.newConfig(testConfigCITest)
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
            }
        }
        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }

    private fun runServerSelection() {
        val config = Config.newConfig(testConfigCITest)
        val configHandler: ConfigHandler
        configHandler = MainThreadConfigHandler(LoggingConfigHandler(output))
        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }

    private fun runTestWithUploadAndTraceroute(speedtestSDK: SpeedtestSDK) {
        val config = Config.newConfig(testConfigCITest)
        config?.tasks = arrayListOf(Task.newCustomThroughputTask(hashSetOf(ThroughputStage.UPLOAD)),
            Task.newServerTracerouteTask())
        val configHandler = object : ConfigHandlerBase() {
            override fun onConfigFetchFinished(validatedConfig: ValidatedConfig?) {
                if (testFinished) {
                    return;
                }
                val handlerWithStageProgression =
                    UiTestHandlerWithStageProgression(output, jsonView)
                val handler = MainThreadTestHandler(handlerWithStageProgression)
                taskManager = speedtestSDK.newTaskManager(handler, validatedConfig)
                taskManager?.start()
            }

            override fun onConfigFetchFailed(error: OoklaError) {
                output.append("Config fetch failed with ${error.message}\n")
            }
        }
        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }

    private fun runTestWithTraceroute(speedtestSDK: SpeedtestSDK) {
        val config = Config.newConfig(testConfigCITest)
        val configHandler: ConfigHandler
        config?.tasks = arrayListOf(Task.newTracerouteTask("www.speedtest.com"),
            Task.newTracerouteTask("www.ookla.com"),
            Task.newServerTracerouteTask(),
            Task.newTimeoutTask(5)
        )
        config?.disableResultUpload = true
        configHandler = object : ConfigHandlerBase() {
            override fun onConfigFetchFinished(validatedConfig: ValidatedConfig?) {
                if (testFinished) {
                    return;
                }
                val handlerWithStageProgression =
                    UiTestHandlerWithStageProgression(output, jsonView)
                val handler = MainThreadTestHandler(handlerWithStageProgression)
                taskManager = speedtestSDK.newTaskManager(handler, validatedConfig)
                taskManager?.start()
            }

            override fun onConfigFetchFailed(error: OoklaError) {
                output.append("Config fetch failed with ${error.message}\n")
            }
        }
        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }

    private fun runTestWithSupplementalData(speedtestSDK: SpeedtestSDK) {
        val config = Config.newConfig(testConfigCITest)
        val configHandler: ConfigHandler
        configHandler = object : ConfigHandlerBase() {
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

                val extraFields = arrayListOf(DataPairs("field", "8918"), DataPairs("otherField", "value"));

                val supplementalData = SupplementalData("1128", "1.0.10", extraFields);
                taskManager = speedtestSDK.newTaskManager(handler, validatedConfig)
                taskManager?.setSupplementalData(supplementalData.toJson().toByteArray())
                taskManager?.start()
            }

            override fun onConfigFetchFailed(error: OoklaError) {
                output.append("Config fetch failed with ${error.message}\n")
            }
        }

        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }

    private fun runBackgroundCaptureDeviceTask(speedtestSDK: SpeedtestSDK) {
        val data = SupplementalData("123", "1.0", arrayListOf())
        val config = Config.newConfig(testConfigBgScan)

        // background
        config?.tasks = arrayListOf(Task.newCaptureDeviceStateTask())

        var backgroundScanTaskManager : TaskManager?
        val configHandler = object : ConfigHandlerBase() {
            override fun onConfigFetchFinished(validatedConfig: ValidatedConfig?) {

                if (testFinished) {

                    return
                }
                val handlerWithStageProgression =
                    UiTestHandlerWithStageProgression(
                        output, jsonView
                    )
                val handler = MainThreadTestHandler(
                    handlerWithStageProgression
                )

                output.text = "Config retrieved over connection type ${validatedConfig?.connectionType.toString()}\n"
                val backgroundScanTaskManagerStatus = speedtestSDK.newTaskManagerWithCreateStatus(handler, validatedConfig)
                backgroundScanTaskManager = backgroundScanTaskManagerStatus.taskManager
                backgroundScanTaskManager?.setSupplementalData(data.toJson().toByteArray())

                if (backgroundScanTaskManagerStatus.didExist()) {
                    output.append("Background task is already running.\n")
                    logLastRunTime(speedtestSDK, testConfigBgScan)
                } else {
                    backgroundScanTaskManager?.start()
                    output.append("Started background task.\n");
                }
            }

            override fun onConfigFetchFailed(error: OoklaError) {
                output.append("Config fetch failed with ${error.message}\n")
            }
        }

        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }

    private fun runBackgroundThroughputTask(speedtestSDK: SpeedtestSDK) {
        val config = Config.newConfig(testConfigBgSpeed)

        // background
        config?.tasks = arrayListOf(Task.newThroughputTask())

        var backgroundThroughputTaskManager : TaskManager?
        val configHandler = object : ConfigHandlerBase() {
            override fun onConfigFetchFinished(validatedConfig: ValidatedConfig?) {
                if (testFinished) {
                    return;
                }
                val handler = MainThreadTestHandler(
                    LoggingTestHandler(output, jsonView)
                )

                output.text = "Config retrieved over connection type ${validatedConfig?.connectionType.toString()}\n"

                val backgroundThroughputTaskManagerStatus = speedtestSDK.newTaskManagerWithAutoAdvance(handler, validatedConfig)
                backgroundThroughputTaskManager = backgroundThroughputTaskManagerStatus.taskManager

                if (backgroundThroughputTaskManagerStatus.didExist()) {
                    output.append("Background task is already running.\n")
                    logLastRunTime(speedtestSDK, testConfigBgScan)
                } else {
                    backgroundThroughputTaskManager?.start()
                    output.append("Started background task.\n");
                }
            }

            override fun onConfigFetchFailed(error: OoklaError) {
                output.append("Config fetch failed with ${error.message}\n")
            }
        }

        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }

    private fun logLastRunTime(speedtestSDK: SpeedtestSDK, name: String) {
        val config = speedtestSDK.configManager
        config.getNamedConfig(name)?.let {
            output.append("\nLast ran at ${it.lastRunTime}\n\n")
        }
    }

    private fun deleteNamedConfigs(speedtestSDK: SpeedtestSDK) {
        val config = speedtestSDK.configManager
        val configs = config.savedConfigs
        configs.forEach {
            output.append("Found saved config ${it.name}\n")
            output.append("Deleting saved config ${it.name}\n")
            config.removeSavedConfig(it.name)
        }

        val configsAfterRemoval = config.savedConfigs
        if (configsAfterRemoval.size == 0) {
            output.append("No saved configs found!\n")
        } else {
            configs.forEach {
                output.append("Found saved config ${it.name}\n")
            }
        }
    }

    private fun reinitSDK(speedtestSDK: SpeedtestSDK) {
        speedtestSDK.terminate()
        SpeedtestSDK.initSDK(application, MainActivity.SPEEDTEST_SDK_API_KEY)

        runShortTest(speedtestSDK)
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
    }

}
