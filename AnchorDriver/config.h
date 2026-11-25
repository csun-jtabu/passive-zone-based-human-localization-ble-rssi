#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>

// Anchor info
extern const int anchorID;  // anchor number
extern String receiverName; // this device's name

// WiFi and BLE Objects
extern WiFiUDP udp;  // This will be the  object that will hold all udp information
extern BLEScan* pointerBLEScan;  // This is the pointer to the BLEScan object
                        // The BLEScan pointer which points to the actual BLEScan object in memory

// WiFi and UDP
extern const char* ssid;  // Wifi name
extern const char* password;  // Wifi password
extern const char* udpAddress;  // Laptop ip address (Broadcasting IP Address is used right now)
extern const int udpPort;  // Randomized udp port between

// BLE scan
extern int scanTime;  // This is the time it takes to scan for BLE devices

// Device names to track
extern String trackedDevices[];  // This will hold the names of the ESP32s we want to track
extern int numDeviceNames;  // This will be the number of device names we are tracking

// Functions
void setupWiFi();
void sendUDP(String currentDevice, int rssi); // To send over Wifi
void setupBLE();  
BLEScanResults* scan(); // This is function we call when we want to scan via BLE
bool checkInList(String deviceName); // Helper method to check if device is in list

#endif