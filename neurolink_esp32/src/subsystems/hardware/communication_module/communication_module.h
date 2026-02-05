#pragma once

namespace neurolink::hardware::communication_module {

class CommunicationModule {
 public:
  void begin();
  void tick();
};

}  // namespace neurolink::hardware::communication_module
