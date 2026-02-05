#pragma once

namespace neurolink::hardware::power_management {

class PowerManagementSystem {
 public:
  void begin();
  void tick();
};

}  // namespace neurolink::hardware::power_management
