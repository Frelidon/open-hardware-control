cmake_minimum_required(VERSION 3.16)
project(ohc_native_openrgb_plugin LANGUAGES CXX)

set(OPENRGB_SOURCE_DIR "" CACHE PATH "OpenRGB source checkout (release_1.1 or newer)")
if(NOT OPENRGB_SOURCE_DIR)
  message(FATAL_ERROR "Set -DOPENRGB_SOURCE_DIR=/path/to/OpenRGB")
endif()

find_package(Qt6 REQUIRED COMPONENTS Core Widgets)
set(CMAKE_AUTOMOC ON)
add_library(ohc_native MODULE OHCNativePlugin.cpp OHCNativePlugin.h)
target_compile_features(ohc_native PRIVATE cxx_std_17)
target_include_directories(ohc_native PRIVATE
  "${OPENRGB_SOURCE_DIR}" "${OPENRGB_SOURCE_DIR}/RGBController")
target_link_libraries(ohc_native PRIVATE Qt6::Core Qt6::Widgets)
set_target_properties(ohc_native PROPERTIES PREFIX "" OUTPUT_NAME "OHCNativePlugin")
