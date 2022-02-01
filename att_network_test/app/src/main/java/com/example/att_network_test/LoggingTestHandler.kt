package com.example.att_network_test

import android.widget.TextView
import com.dandan.jsonhandleview.library.JsonViewLayout
import com.ookla.speedtest.sdk.BackgroundScanResult
import com.ookla.speedtest.sdk.ConfigHandlerBase
import com.ookla.speedtest.sdk.SpeedtestResult
import com.ookla.speedtest.sdk.config.ConfigHandler
import com.ookla.speedtest.sdk.config.ValidatedConfig
import com.ookla.speedtest.sdk.handler.TaskManagerController
import com.ookla.speedtest.sdk.handler.TestHandler
import com.ookla.speedtest.sdk.handler.TestHandlerBase
import com.ookla.speedtest.sdk.model.*
import com.ookla.speedtest.sdk.model.ServerSelection
import com.ookla.speedtest.sdk.result.*
import java.text.SimpleDateFormat
import java.util.*

/**
 * A Speedtest SDK [TestHandler] implementation which logs each of the callback methods to
 * the given [TextView]
 */



private fun removeLastLine(v: TextView) {
    if (v.text == null) {
        return
    }

    val currentValue = v.text.toString()
    val newValue = currentValue.substring(0, currentValue.lastIndexOf("\n", v.text.length - 2) + 1)
    v.text = newValue
}

private fun log(v: TextView, msg: String, update: Boolean = false) {
    val dateFormat = SimpleDateFormat("HH:mm:ss")
    val formattedDate = dateFormat.format(Date())

    val outputText = String.format("%s: %s\n", formattedDate, msg)

    if (update) {
        removeLastLine(v)
    }

    v.append(outputText)
}

open class LoggingTestHandler(private val v: TextView, private val jsonView: JsonViewLayout, private val scheduledSupplementalData: SupplementalDataScheduled? = null, private val resetEachTest : Boolean = false) : TestHandlerBase() {

    var disableOutput: Boolean = false
    var jsonViewBound: Boolean = false

    override fun onTestStarted(taskController: TaskManagerController?) {
        log("onTestStarted")
        // Set supplemental data for the example scheduled test.
        if(scheduledSupplementalData != null) {
            scheduledSupplementalData.startTimestamp = System.currentTimeMillis() / 1000.0
            scheduledSupplementalData.testNumber++
            taskController?.setSupplementalData(scheduledSupplementalData.toJson().toByteArray())
        }
        if (resetEachTest) {
            v.text = ""
        }
        disableOutput = true
    }

    override fun onResultUploadFinished(resultUpload: ResultUpload?, error: OoklaError?) {
        if (error == null && resultUpload?.didSucceed!!) {
            log("onResultUploadFinished - Success: ${resultUpload.httpStatusCode}")
        } else {
            log("onResultUploadFinished - Failure: ${resultUpload?.httpStatusCode}")
            resultUpload?.response?.error?.forEach {
                log("    error: $it")
            }
        }
    }

    override fun onTestFinished(speedtestResult: com.ookla.speedtest.sdk.SpeedtestResult) {
        log("onTestFinished")
        val resultObj = speedtestResult.resultObj
        MainActivity.lastTestGuid = resultObj.guid

        if (!jsonViewBound && !resetEachTest) {
            jsonView.bindJson(resultObj.toJson())
            jsonViewBound = true
        }
    }

    override fun onTestCanceled() {
        log("onTestCanceled")
    }

    override fun onTestFailed(error: OoklaError, speedtestResult: SpeedtestResult?) {
        log("onTestFailed: ${error.message}")
    }

    override fun onThroughputStageStarted(taskController: TaskManagerController?, stage: ThroughputStage) {
        log("onThroughputStageStarted: $stage")
        disableOutput = false
    }

    override fun onThroughputStageFailed(stage: ThroughputStage, error: OoklaError) {
        log("onThroughputStageFailed: ${error.message}")
    }

    override fun onThroughputStageFinished(taskController: TaskManagerController?, stage: ThroughputStage) {
        log("onStageFinished")
    }

    override fun onThroughputTaskStarted(taskController: TaskManagerController?, remoteIp: String, localIp: String) {
        log("onThroughputTaskStarted")
    }

    override fun onThroughputTaskFinished(taskController: TaskManagerController?, result: ThroughputResult) {
        log("onThroughputTaskFinished")
    }

    override fun onPacketlossFinished(taskController: TaskManagerController?, result: PacketlossResult) {
        log("onPacketlossFinished with sent ${result.packetsSent} and received ${result.packetsReceived} ")
    }

    override fun onLatencyProgressUpdated(result: LatencyResult, progressPercentage: Float) {
        val latency = String.format("%.3f", result.latencyMillis / 1000.0)
        log("onLatencyProgressUpdated $latency", disableOutput)

        if (!disableOutput) {
            disableOutput = true
        }
    }

    override fun onLatencyFinished(taskController: TaskManagerController?, result: LatencyResult) {
        log("onLatencyFinished")
    }

    override fun onDownloadProgressUpdated(result: TransferResult, progressPercentage: Float) {
        val speed = String.format("%.3f", result.speedMbps)
        log("onDownloadProgressUpdated $speed Mbps", disableOutput)
        if (!disableOutput) {
            disableOutput = true
        }
    }

    override fun onDownloadFinished(taskController: TaskManagerController?, result: TransferResult) {
        val speed = String.format("%.3f", result.speedMbps)
        log("onDownloadFinished $speed Mbps")
    }

    override fun onUploadProgressUpdated(result: TransferResult, progressPercentage: Float) {
        val speed = String.format("%.3f", result.speedMbps)
        log("onUploadProgressUpdated $speed Mbps", disableOutput)
        if (!disableOutput) {
            disableOutput = true
        }
    }

    override fun onUploadFinished(taskController: TaskManagerController?, result: TransferResult) {
        val speed = String.format("%.3f", result.speedMbps)
        log("onUploadFinished $speed Mbps")
    }

    override fun onTracerouteStarted(taskController: TaskManagerController?, host: String, ip: String) {
        log("onTracerouteStarted")
    }

    override fun onTracerouteHop(host: String, hop: TracerouteHop) {

    }

    override fun onTracerouteFinished(taskController: TaskManagerController?, host: String, traceroute: Traceroute) {
        log("onTracerouteFinished")
    }

    override fun onTracerouteFailed(error: OoklaError, host: String, traceroute: Traceroute?) {
        log("onTracerouteFailed")
    }

    override fun onTracerouteCanceled(host: String) {
        log("onTracerouteCanceled")
    }

    override fun onDeviceStateCaptureFinished(result: BackgroundScanResult) {
        log("onDeviceStateCaptureFinished")

        if (!jsonViewBound && !resetEachTest) {
            jsonView.bindJson(result.resultObj.toJson())
            jsonViewBound = true
        }
    }

    override fun onDeviceStateCaptureFailed(error: OoklaError) {
        log("onDeviceStateCaptureFailed(${error.type}: ${error.message})")
    }

    fun log(msg: String, update: Boolean = false) {
        log(v, msg, update)
    }
}

open class LoggingConfigHandler(private val v: TextView) : ConfigHandlerBase() {

    override fun onConfigFetchFailed(error: OoklaError) {
        log("onConfigFetchFailed(${error.code}: ${error.message} ${error.type}")
    }

    override fun onConfigFetchFinished(config: ValidatedConfig?) {
        log("onConfigFetchFinished()")
    }

    override fun onConfigFetchStarted() {
        log("onConfigFetchStarted()")
    }

    override fun onServerSelectionStarted() {
        log("onServerSelectionStarted()")
    }

    override fun onSelectionFinished(result: ArrayList<ServerSelection>) {
        log("onSelectionFinished(")
        for (sel in result) {
            log(String.format("    %2d: %s @ %s, %s (%s) => %.2f ms", sel.server.id, sel.server.sponsor, sel.server.city, sel.server.country, sel.server.hostname, sel.latencyMillis))
        }
        log(")")
   }

    override fun onSelectionFailed(result: ArrayList<ServerSelection>) {
        log("onSelectionFailed(")
        for (sel in result) {
            log(String.format("    %2d: %s: %s", sel.server.id, sel.server.sponsor, sel.error?.message ?: "[No error cause]"))
        }
        log(")")
    }

    private fun log(msg: String, update: Boolean = false) {
        log(v, msg, update)
    }
}
