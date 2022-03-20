package com.example.att_network_test

import android.Manifest
import android.app.ActivityOptions
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationManager
import android.os.Bundle
import android.provider.Settings
import android.support.v4.os.IResultReceiver
import android.util.Log
import android.widget.AdapterView.OnItemClickListener
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.google.android.gms.location.*
import com.google.firebase.firestore.FieldValue
import com.google.firebase.firestore.FirebaseFirestore
import com.karumi.dexter.Dexter
import com.karumi.dexter.MultiplePermissionsReport
import com.karumi.dexter.PermissionToken
import com.karumi.dexter.listener.PermissionRequest
import com.karumi.dexter.listener.multi.MultiplePermissionsListener
import com.ookla.speedtest.sdk.SpeedtestSDK

import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.coroutines.*

import com.google.firebase.firestore.ktx.firestore
import com.google.firebase.ktx.Firebase
import kotlinx.android.synthetic.main.activity_test.*
import java.lang.RuntimeException


class MainActivity : AppCompatActivity() {

    private var runTest: Boolean? = false
    private lateinit var fusedLocationProviderClient: FusedLocationProviderClient

    private val db = Firebase.firestore



    companion object {
        // Use the key provided to you instead of the test key below
        const val SPEEDTEST_SDK_API_KEY = "o7htwvpp3tycrei1"
        const val SPEEDTEST_SDK_RESULT_KEY = "d7x47854dtlgwi31"
        var lastTestGuid: String? = null
        private const val PERMISSION_ID = 100
        var longitude: Double?= 0.0
        var latitude: Double?=0.0
        var altitude: Double?=0.0
    }



    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        fusedLocationProviderClient=LocationServices.getFusedLocationProviderClient(this)


        checkPermissions()

        val availableTests = TestActivity.TestFunctionality.values()
        val arrayAdapter =
            ArrayAdapter(this, android.R.layout.simple_list_item_1,
                availableTests.map { it.title }.toList())


        actionList.adapter = arrayAdapter
        actionList.onItemClickListener = OnItemClickListener { _, _, position, _ ->
            getCurrentLocation()
            startActivityWith(availableTests[position])
        }

        val shortTest = TestActivity.TestFunctionality.ShortTest



        fun run() {
            //Call your function here
            suspend fun runShortTest() = coroutineScope {
                startActivityWith(shortTest)
            }

            suspend fun getResult() = coroutineScope {
                getCurrentLocation()
            }

            val first = GlobalScope.launch(Dispatchers.Default) {
                runShortTest()
            }
            val second = GlobalScope.launch(Dispatchers.Default) {
                getResult()
            }
            runBlocking {
                first.join()
                second.join()

            }
        }

        val scope= MainScope()
        var job: Job? = null

        fun stopUpdates(){
            job?.cancel()
            job = null
        }

        fun startUpdates() {
            stopUpdates()
            job = scope.launch{
                while(true){
                    run()
                    delay(20000)
                }
            }
        }

        fun listenOnOperation() {
            val docRef = db.collection("operations").document("operate")
            docRef.addSnapshotListener { snapshot, e ->
                if (e != null) {
                    Toast.makeText(this,"Failed",Toast.LENGTH_LONG).show()
                    return@addSnapshotListener
                }

                if (snapshot != null && snapshot.exists()) {
                    Toast.makeText(this, snapshot.data?.get("test").toString(),Toast.LENGTH_LONG).show()
                    runTest = snapshot.data?.get("test") as Boolean?
                    if (runTest == true){
                        startUpdates()
                    }
                    if (runTest == false){
                        stopUpdates()
                    }
                } else {
                }
            }
        }
        listenOnOperation()



        startTest.setOnClickListener { _ ->
            startUpdates()
            Toast.makeText(this,"Start the Auto Test Run",Toast.LENGTH_LONG).show()
        }

        stopTest.setOnClickListener { _ ->
            stopUpdates()
            Toast.makeText(this,"Stopped the Test Run",Toast.LENGTH_LONG).show()
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

    private fun getCurrentLocation(){
        if (checkPermission()){
            if (isLocationEnabled()){
                fusedLocationProviderClient.lastLocation.addOnCompleteListener(this){task->
                    val location:Location?= task.result
                    if (location == null){
                        Toast.makeText(this,"NULL Received",Toast.LENGTH_SHORT).show()
                    }
                    else{
                        latitude = location.latitude
                        longitude = location.longitude
                        altitude = location.altitude
                        Toast.makeText(this,"Longitude: "+longitude.toString()
                            + "\n Latitude: "+ latitude.toString(), Toast.LENGTH_LONG).show()
                        Toast.makeText(this,"Altitude: "+ altitude.toString(), Toast.LENGTH_LONG).show()
//                        Toast.makeText(this,longitude.toString()
//                                + "\n" + latitude.toString()
//                                + "\n"+ altitude.toString(),Toast.LENGTH_LONG).show()
                    }
                }
            }
            else{
                Toast.makeText(this,"Turn on Location",Toast.LENGTH_SHORT).show()
                val intent = Intent(Settings.ACTION_LOCALE_SETTINGS)
                startActivity(intent)
            }
        }
        else{
            requestPermission()
        }
    }
    private fun checkPermission():Boolean{
        if(
            ActivityCompat.checkSelfPermission(this,android.Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED ||
            ActivityCompat.checkSelfPermission(this,android.Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        ){
            return true
        }

        return false
    }

    private fun requestPermission(){
        //this function will allows us to tell the user to requesut the necessary permsiion if they are not garented
        ActivityCompat.requestPermissions(
            this,
            arrayOf(android.Manifest.permission.ACCESS_COARSE_LOCATION,android.Manifest.permission.ACCESS_FINE_LOCATION),
            PERMISSION_ID
        )
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if(requestCode == PERMISSION_ID){
            if(grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED){
                Log.d("Debug:","You have the Permission")
            }
        }
    }


    private fun isLocationEnabled():Boolean{
        //this function will return to us the state of the location service
        //if the gps or the network provider is enabled then it will return true otherwise it will return false
        var locationManager = getSystemService(Context.LOCATION_SERVICE) as LocationManager
        return locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) || locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)
    }

    private fun startActivityWith(functionality: TestActivity.TestFunctionality) {
        val intent = Intent(applicationContext, TestActivity::class.java)
        intent.putExtra("testFunctionality", functionality)

        val options =
            ActivityOptions.makeCustomAnimation(applicationContext, android.R.anim.fade_in, android.R.anim.fade_out)
        this@MainActivity.startActivity(intent, options.toBundle())
    }


    private fun checkPermissions(){
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
            Toast.makeText(
                this@MainActivity,
                "Please enable background location from settings page",
                Toast.LENGTH_SHORT
            ).show();
        }

    }


}
