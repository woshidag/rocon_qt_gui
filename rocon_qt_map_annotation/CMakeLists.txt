cmake_minimum_required(VERSION 2.8.3)
project(rocon_qt_map_annotation)

find_package(catkin REQUIRED)

catkin_python_setup()

catkin_package()

install(
  FILES rocon_map_annotation_plugin.xml
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
install(
   DIRECTORY ui resources
   DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
