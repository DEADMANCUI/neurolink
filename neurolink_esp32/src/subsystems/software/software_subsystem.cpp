#include "software_subsystem.h"

#include "app_layer/app_layer.h"
#include "middleware/middleware.h"
#include "os_layer/os_layer.h"
#include "security_framework/security_framework.h"

namespace neurolink::software {

using app_layer::AppLayer;
using middleware::Middleware;
using os_layer::OsLayer;
using security_framework::SecurityFramework;

namespace {
AppLayer g_app;
SecurityFramework g_security;
Middleware g_middleware;
OsLayer g_os;
}  // namespace

void SoftwareSubsystem::begin() {
  g_os.begin();
  g_security.begin();
  g_middleware.begin();
  g_app.begin();
}

void SoftwareSubsystem::tick() {
  g_os.tick();
  g_security.tick();
  g_middleware.tick();
  g_app.tick();
}

}  // namespace neurolink::software
