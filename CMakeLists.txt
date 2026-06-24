cmake_minimum_required(VERSION 3.20)

project(WinInternals)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")

# Remove /RTC1 (stack corruption check) added by CMake's Debug config globally
string(REPLACE "/RTC1" "" CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG}")

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/common/cmake")

add_subdirectory(exploitation/01_stack_overflow/basic_ret_overwrite)
add_subdirectory(internals/resolve_func_from_peb)
