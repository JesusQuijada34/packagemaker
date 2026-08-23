#include "bridge_protocol.h"

#include <cassert>
#include <string>

int main() {
  using influent::BridgeProtocol;

  const auto ping = BridgeProtocol::handle("PING\n");
  assert(ping.ok);
  assert(ping.payload == "PONG");

  const auto status = BridgeProtocol::handle("STATUS");
  assert(status.ok);
  assert(status.payload.find("aosp-cuttlefish") != std::string::npos);

  const auto launch = BridgeProtocol::handle("LAUNCH com.example.notes");
  assert(launch.ok);
  assert(launch.payload == "LAUNCH_ACCEPTED com.example.notes");

  const auto invalid_package = BridgeProtocol::handle("LAUNCH com..example");
  assert(!invalid_package.ok);
  assert(invalid_package.payload == "INVALID_PACKAGE");

  const auto valid_install = BridgeProtocol::handle("INSTALL /var/lib/influent/apks/notes.apk");
  assert(valid_install.ok);

  const auto traversal = BridgeProtocol::handle("INSTALL /var/lib/influent/apks/../secret.apk");
  assert(!traversal.ok);
  assert(traversal.payload == "INVALID_APK_PATH");

  const auto unknown = BridgeProtocol::handle("SHELL rm -rf /");
  assert(!unknown.ok);
  assert(unknown.payload == "UNKNOWN_COMMAND");
  return 0;
}
