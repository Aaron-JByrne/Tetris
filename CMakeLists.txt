cmake_minimum_required(VERSION 4.0)
project(tetris C)
include_directories(/opt/homebrew/include)

set(CMAKE_C_STANDARD 11)

find_package(SDL2 REQUIRED)
find_package(SDL2_ttf REQUIRED)
include_directories(${SDL2_INCLUDE_DIRS})

add_executable(tetris main.c)
target_link_libraries(tetris ${SDL2_LIBRARIES} SDL2_ttf::SDL2_ttf)