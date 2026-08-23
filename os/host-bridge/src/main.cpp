#include "bridge_protocol.h"
#include "runtime_controller.h"

#include <cerrno>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <iostream>
#include <sstream>
#include <string>

#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>

namespace {

volatile std::sig_atomic_t running = 1;
int server_fd = -1;
std::string socket_path;

void stop_server(int) {
  running = 0;
  if (server_fd >= 0) {
    shutdown(server_fd, SHUT_RDWR);
  }
}

bool write_all(const int fd, const std::string& message) {
  std::size_t written = 0U;
  while (written < message.size()) {
    const ssize_t count = write(fd, message.data() + written, message.size() - written);
    if (count < 0) {
      if (errno == EINTR) {
        continue;
      }
      return false;
    }
    written += static_cast<std::size_t>(count);
  }
  return true;
}

std::string env_or(const char* name, const char* fallback) {
  const char* value = std::getenv(name);
  return value == nullptr ? std::string(fallback) : std::string(value);
}

std::string parse_socket_path(int argc, char** argv) {
  for (int index = 1; index + 1 < argc; ++index) {
    if (std::string(argv[index]) == "--socket") {
      return argv[index + 1];
    }
  }
  return "/run/influent/bridge.sock";
}

influent::CommandResult handle_command(influent::RuntimeController& runtime, const std::string& line) {
  std::istringstream input(line);
  std::string command;
  input >> command;

  if (command == "PING") {
    return {true, "PONG"};
  }
  if (command == "STATUS") {
    return runtime.status();
  }
  if (command == "ANDROID_START") {
    return runtime.start();
  }
  if (command == "ANDROID_STOP") {
    return runtime.stop();
  }
  if (command == "LAUNCH") {
    std::string package_name;
    input >> package_name;
    return runtime.launch(package_name);
  }
  if (command == "INSTALL") {
    std::string apk_path;
    input >> apk_path;
    return runtime.install(apk_path);
  }
  return influent::BridgeProtocol::handle(line);
}

}  // namespace

int main(int argc, char** argv) {
  socket_path = parse_socket_path(argc, argv);
  const std::filesystem::path path(socket_path);
  std::error_code error;
  std::filesystem::create_directories(path.parent_path(), error);
  if (error) {
    std::cerr << "No se pudo crear el directorio del socket: " << error.message() << '\n';
    return 1;
  }

  const std::string adb_binary = env_or("INFLUENT_ADB_BIN", "/usr/bin/adb");
  const std::string serial = env_or("INFLUENT_ANDROID_SERIAL", "localhost:6520");
  const std::string android_home = env_or("INFLUENT_ANDROID_HOME", "/var/lib/influent/android");
  influent::RuntimeController runtime(adb_binary, serial, android_home);

  std::signal(SIGINT, stop_server);
  std::signal(SIGTERM, stop_server);
  std::signal(SIGPIPE, SIG_IGN);

  unlink(socket_path.c_str());
  server_fd = socket(AF_UNIX, SOCK_STREAM, 0);
  if (server_fd < 0) {
    std::cerr << "No se pudo crear el socket: " << std::strerror(errno) << '\n';
    return 2;
  }

  sockaddr_un address{};
  address.sun_family = AF_UNIX;
  if (socket_path.size() >= sizeof(address.sun_path)) {
    std::cerr << "Ruta del socket demasiado larga\n";
    close(server_fd);
    return 3;
  }
  std::strncpy(address.sun_path, socket_path.c_str(), sizeof(address.sun_path) - 1U);

  if (bind(server_fd, reinterpret_cast<sockaddr*>(&address), sizeof(address)) < 0 || listen(server_fd, 16) < 0) {
    std::cerr << "No se pudo publicar el socket: " << std::strerror(errno) << '\n';
    close(server_fd);
    unlink(socket_path.c_str());
    return 4;
  }
  chmod(socket_path.c_str(), 0660);

  std::cout << "influent-bridge escuchando en " << socket_path << '\n';
  while (running != 0) {
    const int client_fd = accept(server_fd, nullptr, nullptr);
    if (client_fd < 0) {
      if (errno == EINTR) {
        continue;
      }
      if (running != 0) {
        std::cerr << "Error aceptando cliente: " << std::strerror(errno) << '\n';
      }
      break;
    }

    char buffer[4096]{};
    const ssize_t count = read(client_fd, buffer, sizeof(buffer) - 1U);
    if (count > 0) {
      const influent::CommandResult result = handle_command(runtime, std::string(buffer, static_cast<std::size_t>(count)));
      const std::string response = (result.ok ? "OK " : "ERROR ") + result.payload + "\n";
      write_all(client_fd, response);
    }
    close(client_fd);
  }

  close(server_fd);
  server_fd = -1;
  unlink(socket_path.c_str());
  return 0;
}
