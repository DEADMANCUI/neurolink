#include <Arduino.h>

#include "subsystems/hardware/hardware_subsystem.h"
#include "subsystems/software/software_subsystem.h"
#include "subsystems/support/support_subsystem.h"
#include "subsystems/network/network_subsystem.h"

using neurolink::hardware::HardwareSubsystem;
using neurolink::network::NetworkSubsystem;
using neurolink::software::SoftwareSubsystem;
using neurolink::support::SupportSubsystem;

HardwareSubsystem g_hardware;
SoftwareSubsystem g_software;
SupportSubsystem g_support;
NetworkSubsystem g_network;

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println("Neurolink ESP32-S3: boot");

  g_hardware.begin();
  g_software.begin();
  g_support.begin();
  g_network.begin();
}

void loop() {
  g_hardware.tick();
  g_software.tick();
  g_support.tick();
  g_network.tick();
}
