
#include <arduino.h>
#include <DHT.h>

const int FLOATING_PIN = 3;
const int TEMP_PIN = 4;

#define DHTTYPE DHT22
DHT dht(TEMP_PIN, DHTTYPE);

void setup() {
    pinMode(FLOATING_PIN, INPUT);
	Serial.begin(9600);
	dht.begin();

}

void loop() {

	// 1 at top, 0 at bottom
	int water = 0; //digitalRead(FLOATING_PIN);

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // check if returns are valid, if they are NaN (not a number) then something went wrong!
  if (isnan(t) || isnan(h)) {
    Serial.println("Failed to read from DHT");
  } else {
    Serial.print("Humidity: "); 
    Serial.print(h);
    Serial.print(" %\t");
    Serial.print("Temperature: "); 
    Serial.print(t);
    Serial.println(" *C");
  }


	//Serial.println(water);

	delay(2000);
}
 
