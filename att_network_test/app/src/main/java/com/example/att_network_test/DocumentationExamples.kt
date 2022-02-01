package com.example.att_network_test
import com.ookla.speedtest.sdk.ConfigHandlerBase
import com.ookla.speedtest.sdk.MainThreadConfigHandler
import com.ookla.speedtest.sdk.SpeedtestSDK
import com.ookla.speedtest.sdk.TaskManager
import com.ookla.speedtest.sdk.config.Config
import com.ookla.speedtest.sdk.config.Task
import com.ookla.speedtest.sdk.config.ValidatedConfig
import com.ookla.speedtest.sdk.handler.MainThreadTestHandler
import com.ookla.speedtest.sdk.handler.TestHandlerBase
import com.ookla.speedtest.sdk.result.OoklaError

/**
 * This class would normally handle the callbacks you're interested in, but is here
 * just to make the example code compile.
 */
class CustomTestHandler : TestHandlerBase()

/**
 * Various usage examples. These are not fully functional and aren't intended to be run, but are here
 * for documentation purposes only.
 */
class DocumentationExamples {
    /**
     * The following example shows how to run a quick test using
     * [ValidatedConfig][com.ookla.speedtest.sdk.config.ValidatedConfig] against a specific server
     * with id 10395.
     *
     * @sample com.ookla.speedtest.sampleapp.DocumentationExamples.quickSingleServerTest
     */
    fun quickSingleServerTest() {
        // Needs prior initialization for this method to work, see documentation of getInstance()
        val speedtestSDK = SpeedtestSDK.getInstance()

        // Create a config which runs a test quickly.
        val config = Config.newConfig("engine-ci-config")
        config?.transferTestDurationSeconds = 5

        // Define a config callback which runs the test after config is downloaded
        val configHandler = object : ConfigHandlerBase() {
            override fun onConfigFetchFinished(validatedConfig: ValidatedConfig?) {
                // override the server we are testing against based on the resultsj
                validatedConfig?.configuration?.serverIdForTesting = 10395
                // testHandler is a custom callback defined by user. Wrap with MainThreadTestHandler
                // to ensure callbacks happen on the main thread.
                val testHandler = MainThreadTestHandler(CustomTestHandler())
                // Create a new task manager and start the test.
                val taskManager = speedtestSDK.newTaskManager(testHandler, validatedConfig)
                taskManager.start()
            }
        }

        // Validate the config which fetches the configuration
        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }

    /**
     * This example configures and starts a named background scan job. The configuration
     * must previously have been configured in Speedtest Custom.
     *
     * @sample com.ookla.speedtest.sampleapp.DocumentationExamples.namedBackgroundTest
     */
    fun namedBackgroundTest() {
        // Needs prior initialization for this method to work, see documentation of getInstance()
        val speedtestSDK = SpeedtestSDK.getInstance()

        // Fetch the named configuration.
        val config = Config.newConfig("engine-signal-scan-config")

        // Configure it to run just a device capture task.
        config?.tasks = arrayListOf(Task.newCaptureDeviceStateTask())

        var backgroundScanTaskManager : TaskManager
        val configHandler = object : ConfigHandlerBase() {
            override fun onConfigFetchFinished(validatedConfig: ValidatedConfig?) {
                // testHandler is a custom callback defined by user
                val testHandler = MainThreadTestHandler(CustomTestHandler())

                backgroundScanTaskManager = speedtestSDK.newTaskManager(testHandler, validatedConfig)

                // ensure that this task is started only once
                if (!backgroundScanTaskManager.isStarted) {
                    backgroundScanTaskManager.start()
                }
            }

            override fun onConfigFetchFailed(error: OoklaError) {
                println("Config fetch failed with ${error.message}")
            }
        }

        ValidatedConfig.validate(config, MainThreadConfigHandler(configHandler))
    }
}