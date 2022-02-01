package com.example.att_network_test

import kotlinx.serialization.*
import kotlinx.serialization.json.Json


@Serializable
/**
 * Example nested object for the supplemental data object.
 */
data class DataPairs (
    var key: String,
    var value: String) {
}

@Serializable
/**
 * One way to provide supplemental data is to make an object like this. The only requirement for the data field is to
 * pass in serialized json object (not array). Although it's easy to use a class like this, you can also also manually
 * generate it, load it from a file or fetch from a web service.
 */
data class SupplementalData (
    var myTestId: String,
    var appVersion: String,
    var extraFields: ArrayList<DataPairs>
) {
    fun toJson(): String { return Json.encodeToString(serializer(), this) }

}

@Serializable
/**
 * You can provide any json object you want as supplemental data. There are no specific requirements on the structure.
 */
data class SupplementalDataScheduled (
    var startTimestamp: Double = 0.0,
    var testNumber: Int = 0
)
{
    fun toJson(): String { return Json.encodeToString(serializer(), this) }
}

