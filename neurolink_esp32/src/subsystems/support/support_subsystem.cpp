#include "support_subsystem.h"

#include "logistics_system/logistics_system.h"
#include "maintenance_system/maintenance_system.h"
#include "training_system/training_system.h"

namespace neurolink::support {

using logistics_system::LogisticsSystem;
using maintenance_system::MaintenanceSystem;
using training_system::TrainingSystem;

namespace {
LogisticsSystem g_logistics;
MaintenanceSystem g_maintenance;
TrainingSystem g_training;
}  // namespace

void SupportSubsystem::begin() {
  g_logistics.begin();
  g_maintenance.begin();
  g_training.begin();
}

void SupportSubsystem::tick() {
  g_logistics.tick();
  g_maintenance.tick();
  g_training.tick();
}

}  // namespace neurolink::support
