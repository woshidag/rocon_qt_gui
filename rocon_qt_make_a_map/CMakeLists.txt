##############################################################################
# CMake
##############################################################################

cmake_minimum_required(VERSION 2.8.3)
project(rocon_qt_make_a_map)

##############################################################################
# Catkin
##############################################################################

find_package(catkin REQUIRED)
catkin_package()
catkin_python_setup()

##############################################################################
# Installs
##############################################################################

install( 
    FILES rocon_make_a_map_plugin.xml 
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)

install(DIRECTORY resources
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
