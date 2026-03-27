#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <BLE2901.h>
#include <cmath>

BLEServer *pServer = NULL;
BLECharacteristic *pCharacteristic = NULL;
BLE2901 *descriptor_2901 = NULL;

bool deviceConnected = false; // Is the device connected

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/
#define SERVICE_UUID        "26478d74-e7d2-48f9-8b20-c10f0fdd20d6"
#define CHARACTERISTIC_UUID "2c8a15df-2c93-4a4b-bb1e-392a74e44864"
#define DEVICE_NAME         "OmnicubePlayer2"

// Button Pins
#define DPAD_UP_PIN D10
#define DPAD_RIGHT_PIN D7
#define DPAD_DOWN_PIN D8
#define DPAD_LEFT_PIN D9
#define BUTTON_B_PIN D6
#define BUTTON_A_PIN D5

// Controller inputs
bool controllerInputsCurrent[6] = {}; // 0 - up, 1 - right, 2 - down, 3 - left, 4 - b, 5 - a
bool controllerInputsOld[6] = {0, 0, 0, 0, 0, 0}; // Used to check for changed inputs

unsigned long inactiveMillis; // Milliseconds since last input
unsigned long offMillis; // Millis since last pressing A + B
#define INACTIVE_POWER_OFF 120 // Ammount of seconds of inactivity to power off
#define ACTIVE_POWER_OFF 2.5 // Ammount of seconds of pushing A + B to power off

class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *pServer) { // When connects to RPi, update connection variable
      deviceConnected = true;
  };

  void onDisconnect(BLEServer *pServer) { // If controller disconnects, update connection variable and start advertising
      deviceConnected = false;
      BLEDevice::startAdvertising(); 
  }
};

void ESPSleep(){
  Serial.flush(); // Clear serial
  esp_deep_sleep_start(); // Start sleeping
}

void setup() {
  setCpuFrequencyMhz(80); // Set to 80MHz to save power

  // Pin Initialization
  pinMode(DPAD_UP_PIN, INPUT_PULLUP);
  pinMode(DPAD_RIGHT_PIN, INPUT_PULLUP);
  pinMode(DPAD_DOWN_PIN, INPUT_PULLUP);
  pinMode(DPAD_LEFT_PIN, INPUT_PULLUP);
  pinMode(BUTTON_A_PIN, INPUT_PULLUP);
  pinMode(BUTTON_B_PIN, INPUT_PULLUP);
  
  // BLE Setup
  BLEDevice::init(DEVICE_NAME);

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic
  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_NOTIFY | BLECharacteristic::PROPERTY_INDICATE
  );

  // Creates BLE Descriptor 0x2902: Client Characteristic Configuration Descriptor (CCCD)
  pCharacteristic->addDescriptor(new BLE2902());

  pService->start();

  // Advertising setup, Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true); // Changed to true to help discovery
  pAdvertising->setMinPreferred(0x06);  
  pAdvertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();
}

void loop() {
  bool inputs_changed = false; // Has inputs changed?
  int data_to_send = 0;

  // Read Sensors. Inverted because of buttons being active low
  controllerInputsCurrent[0] = !digitalRead(DPAD_UP_PIN);
  controllerInputsCurrent[1] = !digitalRead(DPAD_RIGHT_PIN);
  controllerInputsCurrent[2] = !digitalRead(DPAD_DOWN_PIN);
  controllerInputsCurrent[3] = !digitalRead(DPAD_LEFT_PIN);
  controllerInputsCurrent[4] = !digitalRead(BUTTON_B_PIN);
  controllerInputsCurrent[5] = !digitalRead(BUTTON_A_PIN);

  if(!controllerInputsCurrent[4] + !controllerInputsCurrent[5]){ // If A + B is not pressed, update offMillis
    offMillis = millis();
  }

  for(int i = 0; i <= 5; i++){ // Check for Changes
    if(controllerInputsCurrent[i] != controllerInputsOld[i]){
      inputs_changed = true;
    }
    controllerInputsOld[i] = controllerInputsCurrent[i];
  }

  if (inputs_changed) { // Send data if inputs changed
    inactiveMillis = millis(); // Update time since last input
    for(int i = 0; i <= 5; i++){ // Format the data into an int (eg 010011 would be up + right + b)
      data_to_send += controllerInputsCurrent[i] * pow(10, i);
    }
    if (deviceConnected) {//Sends data
      pCharacteristic->setValue((uint8_t *)&data_to_send, 4);
      pCharacteristic->notify();
    }
  }
  if(millis()-offMillis > ACTIVE_POWER_OFF * 1000 || millis()-inactiveMillis > INACTIVE_POWER_OFF * 1000){
    ESPSleep();
  }
}
