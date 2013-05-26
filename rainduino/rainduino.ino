
#include <arduino.h>
#include <DHT.h>
#include <SD.h>
#include "sensors.h"


/**
 * General pin configuration
 */
const int FLOATING_PIN = 3;
const int TEMP_PIN = 2;
const int SD_CS_PIN = 4;
const int BED_LIGHT_PIN = A1;
const int PANEL_LIGHT_PIN = A2;
const int MOISTURE_VOLTAGE1 = 8;
const int MOISTURE_VOLTAGE2 = 9;
const int MOISTURE_PIN = A0;
const int PUMP_PIN = 5;

/**
 * Delay for moisture reading
 */
const int MOISTURE_DELAY = 1000;
const int PUMPING_DELAY = 5000;
//const int READING_DELAY = 300000; 
const int READING_DELAY = 5000;

/**
 * DHT22 temperature and humidity sensor
 */
#define DHTTYPE DHT22
DHT dht(TEMP_PIN, DHTTYPE);

/**
 * Operational variables
 */
bool isPumpRunning = false;
int sessionId = 0;
unsigned long lastReading = 0;

void setup() {
	// initialize pins
	// read trigger values from EEPROM
	
	// Initialize pins
    pinMode(FLOATING_PIN, INPUT);
	pinMode(SD_CS_PIN, OUTPUT);
	pinMode(MOISTURE_VOLTAGE1, OUTPUT);
	pinMode(MOISTURE_VOLTAGE2, OUTPUT);
	pinMode(MOISTURE_PIN, INPUT);
	pinMode(PANEL_LIGHT_PIN, INPUT);
	pinMode(BED_LIGHT_PIN, INPUT);

	// Initialize serial and wait until ready
	Serial.begin(9600);
	while (!Serial) { ; }
	
	// Initialize DHT22
	dht.begin();

	// Initialize SD card
	SD.begin(SD_CS_PIN);

}

void loop() {
	// take readings
	// read serial
	//   change settings if needed
	// write readings

	// 1 at top, 0 at bottom
	int water = digitalRead(FLOATING_PIN);
	
	int moisture = readMoisture(4);

	// logic to start or stop pumping goes here
	
	if (lastReading < millis() - READING_DELAY) { 
		// temp and humidity
		float humidity = dht.readHumidity();
		float temperature = dht.readTemperature(true);

		// light
		int panelLight = analogRead(PANEL_LIGHT_PIN);
		int bedLight = analogRead(BED_LIGHT_PIN);
	

		/* * * * Write out readings * * * */
		String start = String(sessionId); 
		start += ":";
		start += millis();
		start += ":";

		String lines[] = { String(start), String(start), String(start), String(start), String(start), String(start) };	
		
		lines[0] += buildLine(SENSOR_PNL_LIGHT_LVL, panelLight);
		lines[1] += buildLine(SENSOR_BED_LIGHT_LVL, bedLight);
		lines[2] += buildLine(SENSOR_BED_MOISTURE, moisture);
		lines[3] += buildLine(SENSOR_BED_HUMIDITY, humidity);
		lines[4] += buildLine(SENSOR_BED_TEMPERATURE, temperature);
		lines[5] += buildLine(SENSOR_WATER_LEVEL, water);

		File file = SD.open("readings.txt", FILE_WRITE);
		
		for (int i = 0; i < 6; i++) {
			if (file) {
				file.println(lines[i]);
			}
			Serial.print("=");
			Serial.println(lines[i]);
		}

		if (file) {
			file.close();
		}
		
		lastReading = millis();
	}

	if (isPumpRunning) {
		delay(PUMPING_DELAY);
	} else {
		delay(READING_DELAY);
	}

}

String buildLine(int sensorId, int value) {
	String ret = String(sensorId);
	ret += ":";
	ret += value;
	return ret;
}

String buildLine(int sensorId, float value, int precision) {
	String ret = String(sensorId);
	ret += ":";
	ret += int(value);
	ret += ".";
	ret += int(abs(int(value) - value) * precision);
	return ret;
}

String buildLine(int sensorId, float value) {
	return buildLine(sensorId, value, 4);
}

String buildLine(int sensorId, bool value) {
	String ret = String(sensorId);
	ret += ":";
	ret += (value) ? '1' : '0';
	return ret;
}

int readMoisture(int samples) {
	bool flip = true;
	int readings = 0;

	for (int i = 0; i < samples; i++) {
		flip = i % 2 == 0;
		setSensorPolarity(flip);
		delay(MOISTURE_DELAY);

		if (flip) {
			readings += analogRead(MOISTURE_PIN);
		} else {
			readings += 1023 - analogRead(MOISTURE_PIN);
		}
	}

	digitalWrite(MOISTURE_VOLTAGE1, LOW);
	digitalWrite(MOISTURE_VOLTAGE2, LOW);

	return readings / samples;

}

/**
 * Set the polarity of the moisture sensor
 */
void setSensorPolarity(bool flip) {
	if (flip) {
		digitalWrite(MOISTURE_VOLTAGE1, HIGH);
		digitalWrite(MOISTURE_VOLTAGE2, LOW);
	} else {
		digitalWrite(MOISTURE_VOLTAGE1, LOW);
		digitalWrite(MOISTURE_VOLTAGE2, HIGH);
	}
}

