#include "network_subsystem.h"

#include "data_distribution/data_distribution.h"
#include "network_management/network_management.h"
#include "protocol_stack/protocol_stack.h"

namespace neurolink::network {

using data_distribution::DataDistributionService;
using network_management::NetworkManagement;
using protocol_stack::ProtocolStack;

namespace {
DataDistributionService g_data_distribution;
NetworkManagement g_network_mgmt;
ProtocolStack g_protocol_stack;
}  // namespace

void NetworkSubsystem::begin() {
  g_protocol_stack.begin();
  g_network_mgmt.begin();
  g_data_distribution.begin();
}

void NetworkSubsystem::tick() {
  g_protocol_stack.tick();
  g_network_mgmt.tick();
  g_data_distribution.tick();
}

}  // namespace neurolink::network
