#pragma once

#include "bridge_protocol.h"

#include <string>
#include <string_view>
#include <vector>

namespace influent {

class RuntimeController final {
 public:
  RuntimeController(std::string adb_binary, std::string serial, std::string cvd_home);

  CommandResult start();
  CommandResult stop();
  CommandResult status() const;
  CommandResult launch(std::string_view package_name) const;
  CommandResult install(std::string_view apk_path) const;

 private:
  CommandResult run(const std::string& binary, const std::vector<std::string>& arguments) const;
  std::string adb_target() const;

  std::string adb_binary_;
  std::string serial_;
  std::string cvd_home_;
};

}  // namespace influent
