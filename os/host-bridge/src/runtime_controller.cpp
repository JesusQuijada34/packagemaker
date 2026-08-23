#include "runtime_controller.h"

#include <cerrno>
#include <cstring>
#include <sys/wait.h>
#include <unistd.h>

#include <algorithm>
#include <sstream>

namespace influent {

RuntimeController::RuntimeController(std::string adb_binary, std::string serial, std::string cvd_home)
    : adb_binary_(std::move(adb_binary)), serial_(std::move(serial)), cvd_home_(std::move(cvd_home)) {}

std::string RuntimeController::adb_target() const {
  return serial_.empty() ? std::string{} : "-s";
}

CommandResult RuntimeController::run(const std::string& binary, const std::vector<std::string>& arguments) const {
  int output_pipe[2]{};
  if (pipe(output_pipe) != 0) {
    return {false, "PIPE_FAILED"};
  }

  const pid_t child = fork();
  if (child < 0) {
    close(output_pipe[0]);
    close(output_pipe[1]);
    return {false, "FORK_FAILED"};
  }

  if (child == 0) {
    close(output_pipe[0]);
    dup2(output_pipe[1], STDOUT_FILENO);
    dup2(output_pipe[1], STDERR_FILENO);
    close(output_pipe[1]);
    if (!cvd_home_.empty()) {
      setenv("HOME", cvd_home_.c_str(), 1);
    }

    std::vector<char*> argv;
    argv.reserve(arguments.size() + 2U);
    argv.push_back(const_cast<char*>(binary.c_str()));
    for (const std::string& argument : arguments) {
      argv.push_back(const_cast<char*>(argument.c_str()));
    }
    argv.push_back(nullptr);
    execv(binary.c_str(), argv.data());
    _exit(127);
  }

  close(output_pipe[1]);
  std::string output;
  char buffer[1024]{};
  ssize_t count = 0;
  while ((count = read(output_pipe[0], buffer, sizeof(buffer))) > 0) {
    output.append(buffer, static_cast<std::size_t>(count));
    if (output.size() > 4096U) {
      output.resize(4096U);
      break;
    }
  }
  close(output_pipe[0]);

  int status = 0;
  if (waitpid(child, &status, 0) < 0) {
    return {false, "WAIT_FAILED"};
  }
  if (!WIFEXITED(status) || WEXITSTATUS(status) != 0) {
    std::ostringstream response;
    response << "PROCESS_FAILED " << (WIFEXITED(status) ? WEXITSTATUS(status) : 255);
    if (!output.empty()) {
      response << " " << output;
    }
    return {false, response.str()};
  }
  return {true, output.empty() ? "DONE" : output};
}

CommandResult RuntimeController::start() {
  return run(cvd_home_ + "/bin/launch_cvd", {"--daemon"});
}

CommandResult RuntimeController::stop() {
  return run(cvd_home_ + "/bin/stop_cvd", {});
}

CommandResult RuntimeController::status() const {
  std::vector<std::string> arguments;
  if (!serial_.empty()) {
    arguments.push_back("-s");
    arguments.push_back(serial_);
  }
  arguments.push_back("get-state");
  return run(adb_binary_, arguments);
}

CommandResult RuntimeController::launch(const std::string_view package_name) const {
  const auto validation = BridgeProtocol::handle(std::string("LAUNCH ") + std::string(package_name));
  if (!validation.ok) {
    return validation;
  }
  std::vector<std::string> arguments;
  if (!serial_.empty()) {
    arguments.push_back("-s");
    arguments.push_back(serial_);
  }
  arguments.insert(arguments.end(), {"shell", "am", "start", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", "-p", std::string(package_name)});
  return run(adb_binary_, arguments);
}

CommandResult RuntimeController::install(const std::string_view apk_path) const {
  const auto validation = BridgeProtocol::handle(std::string("INSTALL ") + std::string(apk_path));
  if (!validation.ok) {
    return validation;
  }
  std::vector<std::string> arguments;
  if (!serial_.empty()) {
    arguments.push_back("-s");
    arguments.push_back(serial_);
  }
  arguments.insert(arguments.end(), {"install", "-r", std::string(apk_path)});
  return run(adb_binary_, arguments);
}

}  // namespace influent
