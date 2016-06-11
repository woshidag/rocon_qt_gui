#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/robotics-in-concert/rocon_qt_gui/license/LICENSE
#
##############################################################################
# Imports
##############################################################################

from __future__ import division
import os
import math

from python_qt_binding import loadUi
from python_qt_binding.QtCore import Qt, pyqtSlot
from python_qt_binding.QtGui import QWidget

from qt_gui.plugin import Plugin
import rospkg
import rospy

from rocon_qt_library.widgets import QResourceChooser, QVideoTeleop, QSlamWidget
from rocon_qt_library.interfaces import ResourceChooserInterface, SlamWidgetInterface
##############################################################################
# MakeAMap
##############################################################################
from rocon_console import console

class MakeAMap(Plugin):
    def __init__(self, context):
        self._context = context
        super(MakeAMap, self).__init__(context)
        # I'd like these to be also configurable via the gui
        self._widget = QWidget()
        rospack = rospkg.RosPack()
        ui_file = os.path.join(rospack.get_path('concert_qt_make_a_map'), 'ui', 'concert_make_a_map.ui')
        loadUi(ui_file, self._widget, {'QResourceChooser': QResourceChooser, 'QVideoTeleop': QVideoTeleop, 'QSlamWidget': QSlamWidget})

        # self._widget = QVideoTeleop()
        # if context.serial_number() > 1:
        #     self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        context.add_widget(self._widget)

        self._default_cmd_vel_topic = '/teleop/cmd_vel'
        self._default_compressed_image_topic = '/teleop/compressed_image'
        self._default_map_topic = 'map'
        self._default_scan_topic = '/make_a_map/scan'
        self._default_robot_pose = 'robot_pose'
        self._default_wc_namespace_param = 'wc_namespace'
        self._default_wc_namespace = 'world_canvas'

        # self._default_cmd_vel_topic = 'cmd_vel'
        # self._default_compressed_image_topic = 'compressed_image'
        self._widget.video_teleop_widget.init_teleop_interface(self._default_cmd_vel_topic, self._default_compressed_image_topic)

        scan_slot = self._widget.slam_widget.draw_scan
        robot_pose_slot = self._widget.slam_widget.draw_robot_pose
        # scan_topic = self._get_remaps(self._default_scan_topic, msg.remappings)
        # robot_pose_topic = self._get_remaps(self._default_robot_pose, msg.remappings)
        # wc_namespace_param = rospy.get_param('~wc_namespace_param')
        wc_namespace = rospy.get_param('/name')
        self._default_robot_pose = wc_namespace + '/' + self._default_robot_pose
        console.logdebug("self._default_robot_pose = %s " % self._default_robot_pose)
        map_saved_callbacks = [self._widget.slam_widget.map_saved_callback]
        self._widget.slam_widget.init_slam_widget_interface(map_topic=self._default_map_topic,
                                                                scan_received_slot=scan_slot,
                                                                scan_topic=self._default_scan_topic,
                                                                robot_pose_received_slot=robot_pose_slot,
                                                                robot_pose_topic=self._default_robot_pose,
                                                                wc_namespace=wc_namespace,
                                                                map_saved_callbacks=map_saved_callbacks)

        scene_slot = self._widget.slam_widget.draw_scene
        self._widget.slam_widget.init_map_annotation_interface(scene_update_slot=scene_slot,
            wc_namespace=wc_namespace
            )

    def shutdown_plugin(self):
        # self._widget.shutdown_plugin()
        self._widget.slam_widget.unset_slam_interface()
        self._widget.video_teleop_widget.reset()
