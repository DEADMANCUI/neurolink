#pragma once

namespace neurolink::hardware::hmi_unit {

class HmiUnit {
 public:
  void begin();
  void tick();
};

}  // namespace neurolink::hardware::hmi_unit
