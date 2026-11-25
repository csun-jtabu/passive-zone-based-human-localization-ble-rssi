#include "config.h"

// WiFi Settings
const char* ssid = "insert wifi device name"; 
const char* password = "insert wifi device password"; 
const char* udpAddress = "insert laptop/central processing unit ip address"; 
const int udpPort = 6700;
WiFiUDP udp;

// Anchor Info and Settings
const int anchorID = 4;
String receiverName = "Anchor_" + String(anchorID);

// BLE scan settings
int scanTime = 5;
BLEScan* pointerBLEScan;

// Device names that are being tracked
String trackedDevices[] = {
    "Anchor_1",
    "Anchor_2",
    "Anchor_3",
    "Anchor_4",
    "P8b"
};

int numDeviceNames = sizeof(trackedDevices) / sizeof(trackedDevices[0]);

// Related to WiFi ---------------------------------------------
void setupWiFi()
{
  WiFi.begin(ssid, password); // This begins broadcasting packets to Router

  // This forces the program to wait until we have connection between ESP32 and the Arduino IDE Serial Monitor over WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // This is just confirmation that we are connected to the ESP32 over wifi
  Serial.println("\nWiFi Connected!");
  Serial.println("This is my ESP32 IP Address: " + WiFi.localIP().toString());

  // this starts sending out packets over WiFi
  udp.begin(udpPort);
}

// To send over Wifi
void sendUDP(String currentDevice, int rssi)
{
    // we build the packet to be transmitted over wifi
    // we send the device name of this anchor, the device name of the transmitting anchor, and the rssi value between the anchors
    String packet = receiverName + "," + currentDevice + "," + String(rssi);
    
    // we create a packet that is being sent to a device (in case it's being broadcasted. and the port number)
    udp.beginPacket(udpAddress, udpPort);
    
    // we add our message/data to the packet
    udp.print(packet);

    // we send the packet out
    udp.endPacket();
}
// ------------------------------------------------------------------------------------------

// Related to BLE ---------------------------------------------
void startAdvertising()
{
  
  // this creates the advertising packet
  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();

  // Makes sure name is included in all advertisements:
  BLEAdvertisementData advData;
  advData.setName(receiverName.c_str());
  pAdvertising->setAdvertisementData(advData);


  // this just broadcasts data to anyone listening for a set interval
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinInterval(100);
  pAdvertising->setMaxInterval(200);

  // this starts the advertising
  pAdvertising->start();
  Serial.println("ESP32 is Advertising");
}

void setupBLE()
{
  // we set up the BLE on the ESP32 by first initializing it using its static method
  BLEDevice::init(("Anchor_" + String(anchorID)).c_str());

  // we create the scanner. The BLEScan object will be used to look for BLE Devices
  pointerBLEScan = BLEDevice::getScan();

  // we make the scanner actively sought for packets
  pointerBLEScan -> setActiveScan(true);

  // we set the interval and scan window in milliseconds 
  pointerBLEScan->setInterval(100);
  pointerBLEScan->setWindow(99);         
  Serial.println("ESP32 is ready for scanning");
  startAdvertising();
}

// This is function we call when we want to scan via BLE
BLEScanResults* scan()
{
  // we start the scanner and the scanner will scan for a set amount of time.
  // Essentially we'll record all devices found
  Serial.println("Scanning...");
  BLEScanResults* devicesFound = pointerBLEScan->start(scanTime, false);
  
  // we keep track of the number of devices we find nearby
  int count = devicesFound->getCount();

  // we print out how many devices that were found
  Serial.printf("Devices found: %d\n", count);    

  return devicesFound;
}
//------------------------------------------------------------------------------------------

// Helper Method ----------------------------------------------
bool checkInList(String deviceName)
{
    // we go through each device in the list to see if the deviceName is in it.
    // if it is, then we mark the inList variable as true
    for (int j = 0; j < numDeviceNames; j++)
    {
      String tracked = trackedDevices[j];

      if (deviceName.equals(tracked))
      {
        return true;
      }
    }
    return false;
}
//------------------------------------------------------------------------------------------