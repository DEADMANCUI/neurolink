#pragma once

namespace neurolink::network::protocol_stack {

class ProtocolStack {
 public:
  void begin();
  void tick();
};

}  // namespace neurolink::network::protocol_stack
