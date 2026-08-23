#include "bridge_protocol.h"

#include <cctype>
#include <sstream>

namespace influent {
namespace {

std::string trim(std::string value) {
  const auto first = value.find_first_not_of(" \t\r\n");
  if (first == std::string::npos) {
    return {};
  }
  const auto last = value.find_last_not_of(" \t\r\n");
  return value.substr(first, last - first + 1);
}

}  // namespace

bool BridgeProtocol::valid_package_name(std::string_view package_name) {
  if (package_name.empty() || package_name.size() > 255U || package_name.front() == '.' || package_name.back() == '.') {
    return false;
  }

  bool previous_dot = false;
  for (const char character : package_name) {
    const bool is_valid = std::isalnum(static_cast<unsigned char>(character)) != 0 || character == '_' || character == '.';
    if (!is_valid || (character == '.' && previous_dot)) {
      return false;
    }
    previous_dot = character == '.';
  }
  return true;
}

bool BridgeProtocol::valid_apk_path(std::string_view path) {
  constexpr std::string_view allowed_prefix = "/var/lib/influent/apks/";
  if (path.size() <= allowed_prefix.size() || path.substr(0, allowed_prefix.size()) != allowed_prefix || path.find("..") != std::string_view::npos) {
    return false;
  }
  return path.size() >= 4U && path.substr(path.size() - 4U) == ".apk";
}

CommandResult BridgeProtocol::handle(const std::string_view line) {
  const std::string command_line = trim(std::string(line));
  std::istringstream input(command_line);
  std::string command;
  input >> command;

  if (command == "PING") {
    return {true, "PONG"};
  }
  if (command == "STATUS") {
    return {true, "{\"runtime\":\"aosp-cuttlefish\",\"state\":\"managed\",\"transport\":\"adb\"}"};
  }
  if (command == "ANDROID_START") {
    return {true, "ANDROID_START_ACCEPTED"};
  }
  if (command == "ANDROID_STOP") {
    return {true, "ANDROID_STOP_ACCEPTED"};
  }
  if (command == "LAUNCH") {
    std::string package_name;
    input >> package_name;
    if (!valid_package_name(package_name)) {
      return {false, "INVALID_PACKAGE"};
    }
    return {true, "LAUNCH_ACCEPTED " + package_name};
  }
  if (command == "INSTALL") {
    std::string apk_path;
    input >> apk_path;
    if (!valid_apk_path(apk_path)) {
      return {false, "INVALID_APK_PATH"};
    }
    return {true, "INSTALL_ACCEPTED " + apk_path};
  }

  return {false, "UNKNOWN_COMMAND"};
}

}  // namespace influent
