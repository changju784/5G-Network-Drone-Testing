package com.example.att_network_test

import android.Manifest
import android.app.ActivityOptions
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.AdapterView.OnItemClickListener
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.karumi.dexter.Dexter
import com.karumi.dexter.MultiplePermissionsReport
import com.karumi.dexter.PermissionToken
import com.karumi.dexter.listener.PermissionRequest
import com.karumi.dexter.listener.multi.MultiplePermissionsListener
import com.ookla.speedtest.sdk.SpeedtestSDK

import kotlinx.android.synthetic.main.activity_main.*




class MainActivity : AppCompatActivity() {

    companion object {
        // Use the key provided to you instead of the test key below
        const val SPEEDTEST_SDK_API_KEY = "o7htwvpp3tycrei1"
        const val SPEEDTEST_SDK_RESULT_KEY = "d7x47854dtlgwi31"
        var lastTestGuid: String? = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        checkPermissions()

        val availableTests = TestActivity.TestFunctionality.values()
        val arrayAdapter =
            ArrayAdapter(this, android.R.layout.simple_list_item_1,
                availableTests.map { it.title }.toList())

        actionList.adapter = arrayAdapter
        actionList.onItemClickListener = OnItemClickListener { _, _, position, _ ->
            startActivityWith(availableTests[position])
        }

        foregroundSwitch.isChecked = SpeedtestSDK.getInstance().getSpeedtestSDKOptions().foregroundServiceOption.enabled
        foregroundSwitch.setOnCheckedChangeListener { _, enabled ->
            SpeedtestSDK.getInstance().updateForgroundServiceOption(SpeedtestSDK.ForegroundServiceOption(
                enabled,
                "com.ookla.speedtest.sampleapp.MainActivity",
                "Ookla Sample SDK", "Enabling foreground service to keep the sample SDK always running"))
        }

        locationSwitch.isChecked = SpeedtestSDK.getInstance().getSpeedtestSDKOptions().locationUpdateOption.enableActiveLocation
        locationSwitch.setOnCheckedChangeListener { _, enabled ->
            SpeedtestSDK.getInstance().updateActiveLocationOption(SpeedtestSDK.LocationUpdateOption(
                enabled,
                10
            ))
        }
    }

    private fun startActivityWith(functionality: TestActivity.TestFunctionality) {
        val intent = Intent(applicationContext, TestActivity::class.java)
        intent.putExtra("testFunctionality", functionality)

        val options =
            ActivityOptions.makeCustomAnimation(applicationContext, android.R.anim.fade_in, android.R.anim.fade_out)
        this@MainActivity.startActivity(intent, options.toBundle())
    }

    private fun checkPermissions() {
        var permissionsNeeded = SpeedtestSDK.getInstance().checkPermissions(applicationContext)
        if (permissionsNeeded.isNotEmpty()) {
            Dexter.withContext(this)
                .withPermissions(
                    permissionsNeeded
                ).withListener(object : MultiplePermissionsListener {
                    override fun onPermissionsChecked(report: MultiplePermissionsReport?) {
                        if (true == report?.deniedPermissionResponses?.any {
                            it.permissionName == Manifest.permission.ACCESS_BACKGROUND_LOCATION
                        }) {
                            Dexter.withContext(this@MainActivity)
                                .withPermissions(
                                    Manifest.permission.ACCESS_BACKGROUND_LOCATION
                                ).withListener(multiplePermissionsListener).check()
                        }
                    }

                    override fun onPermissionRationaleShouldBeShown(
                        p0: MutableList<PermissionRequest>?,
                        p1: PermissionToken?
                    ) {
                    }

                }).check()
        }
    }

    val multiplePermissionsListener = object: MultiplePermissionsListener {
        override fun onPermissionsChecked(p0: MultiplePermissionsReport?) {
        }

        override fun onPermissionRationaleShouldBeShown(
            p0: MutableList<PermissionRequest>?,
            p1: PermissionToken?
        ) {
            Toast.makeText(this@MainActivity,"Please enable background location from settings page", Toast.LENGTH_SHORT).show();
        }

    }
}
