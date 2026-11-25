#include "config.h"

void setup() {

  Serial.begin(115200); // Initialize the output from USB
  setupWiFi();
  setupBLE();
}

void loop() {
  
  // We scan for devices
  BLEScanResults* devicesFound = scan();

  // we keep track of the number of devices we find nearby
  int count = devicesFound->getCount();

  // for each device found, we check to see if it matches the device name we are looking for
  for (int i = 0; i < count; i++) {
    BLEAdvertisedDevice device = devicesFound->getDevice(i);

    // if the device doesn't have a name, we skip it
    if (!device.haveName()) 
    {
      continue;
    }

    // This will be used to store the current BLE Device name
    String currentName = device.getName().c_str();

    // if we find the target device
    if (checkInList(currentName) == true)
    {
      // this is the rssi of the device
      int rssi = device.getRSSI();

      // this will be the output on Serial Monitor when we plug it into the arduino
      Serial.printf("Receiver: %s, Transmitter: %s, RSSI: %d dBm\n",
                    receiverName.c_str(),
                    currentName.c_str(),
                    rssi);
      
      // send to computer over WiFi
      sendUDP(currentName, rssi);
    } 
  }
  
  // clears memory 
  pointerBLEScan->clearResults();

  //delays slightly until next scan interval
  delay(5); 
}