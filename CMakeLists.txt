cmake_minimum_required(VERSION 3.10)
project(PestDetection)

set(CMAKE_CXX_STANDARD 14)

# Find OpenCV package
find_package(OpenCV REQUIRED)

# Include OpenCV directories
include_directories(${OpenCV_INCLUDE_DIRS})

# Create executable
add_executable(pest_detect main.cpp)

# Link OpenCV libraries
target_link_libraries(pest_detect ${OpenCV_LIBS})
