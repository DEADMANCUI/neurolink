#include "hardware_subsystem.h"

#include "communication_module/communication_module.h"
#include "core_processing_unit/core_processing_unit.h"
#include "hmi_unit/hmi_unit.h"
#include "power_management/power_management.h"
#include "protection_structure/protection_structure.h"
#include "sensor_suite/sensor_suite.h"

namespace neurolink::hardware {

using communication_module::CommunicationModule;
using core_processing_unit::CoreProcessingUnit;
using hmi_unit::HmiUnit;
using power_management::PowerManagementSystem;
using protection_structure::ProtectionStructure;
using sensor_suite::SensorSuite;

namespace {
ProtectionStructure g_protection;
PowerManagementSystem g_power;
HmiUnit g_hmi;
CommunicationModule g_comm;
SensorSuite g_sensors;
CoreProcessingUnit g_cpu;
}  // namespace

void HardwareSubsystem::begin() {
  g_protection.begin();
  g_power.begin();
  g_hmi.begin();
  g_comm.begin();
  g_sensors.begin();
  g_cpu.begin();
}

void HardwareSubsystem::tick() {
  g_protection.tick();
  g_power.tick();
  g_hmi.tick();
  g_comm.tick();
  g_sensors.tick();
  g_cpu.tick();
}

}  // namespace neurolink::hardware
