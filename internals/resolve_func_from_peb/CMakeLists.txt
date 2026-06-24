cmake_minimum_required(VERSION 3.20)
project(resolve_func_from_peb C)
include(exploit_target)
add_internals_executable(${PROJECT_NAME} main.c)
