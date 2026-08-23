cmake_minimum_required(VERSION 3.16)
project(influent_bridge VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)

add_library(influent_bridge_core
  src/bridge_protocol.cpp
  src/runtime_controller.cpp
)
target_include_directories(influent_bridge_core PUBLIC include)
target_compile_options(influent_bridge_core PRIVATE -Wall -Wextra -Wpedantic -Wconversion)

add_executable(influent-bridge
  src/main.cpp
)
target_link_libraries(influent-bridge PRIVATE influent_bridge_core)
target_compile_options(influent-bridge PRIVATE -Wall -Wextra -Wpedantic -Wconversion)

include(CTest)
if(BUILD_TESTING)
  add_executable(bridge_smoke_test tests/bridge_smoke_test.cpp)
  target_link_libraries(bridge_smoke_test PRIVATE influent_bridge_core)
  target_compile_options(bridge_smoke_test PRIVATE -Wall -Wextra -Wpedantic -Wconversion)
  add_test(NAME bridge_smoke_test COMMAND bridge_smoke_test)
endif()

install(TARGETS influent-bridge RUNTIME DESTINATION usr/lib/influent)
install(FILES include/bridge_protocol.h DESTINATION usr/include/influent)
