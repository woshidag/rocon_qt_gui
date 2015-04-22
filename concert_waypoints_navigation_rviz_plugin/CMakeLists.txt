cmake_minimum_required(VERSION 2.8.3)
project(concert_waypoints_navigation_rviz_plugin)

## Find catkin macros and libraries
## if COMPONENTS list like find_package(catkin REQUIRED COMPONENTS xyz)
## is used, also find other catkin packages
find_package(catkin REQUIRED COMPONENTS
  concert_msgs
  concert_service_msgs
  roscpp
  rviz
)

find_package(Qt4 COMPONENTS QtCore QtGui REQUIRED)
include(${QT_USE_FILE})

add_definitions(-DQT_NO_KEYWORDS)

catkin_package(
  INCLUDE_DIRS include
  LIBRARIES ${PROJECT_NAME}
  CATKIN_DEPENDS concert_msgs concert_service_msgs roscpp rviz
)

include_directories(
  include
  ${catkin_INCLUDE_DIRS}
  ${QT_INCLUDE_DIRS}
)

qt4_wrap_cpp(MOC_FILES
  include/${PROJECT_NAME}/waypoint_navigation_display.h
)

qt4_wrap_ui(UIC_FILES
  ui/waypoint_navigation.ui
)

#include_directories
