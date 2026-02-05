#pragma once

namespace neurolink::hardware::sensor_suite {

class SensorSuite {
 public:
  void begin();
  void tick();
};

}  // namespace neurolink::hardware::sensor_suite
