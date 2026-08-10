import time
from dataclasses import dataclass
from rtde_control import RTDEControlInterface as RTDEControl
from rtde_receive import RTDEReceiveInterface as RTDEReceive
import math
import numpy as np

#Bottom Coupon

ROBOT_IP = "192.168.1.100"
ACCEL = 0.1  # m/s^2
VEL = 0.05
rtde_c = RTDEControl(ROBOT_IP)
rtde_r = RTDEReceive(ROBOT_IP)
current_pos = rtde_r.getActualTCPPose()[:6]

def BrogiBox():
    pose1 = [0.34807241863598354, 0.0408351029625623, 0.5348242964224846, -2.1591464657867423, 0.039864854978964824, -2.1520962658570983]
    target_pose = rtde_c.moveL(pose1, VEL, ACCEL)
    current_pos = rtde_r.getActualTCPPose()[:3]

    pose2 = [0.6216737868085882, 0.04761553081567805, 0.3152049226774737, -2.159147388725588, 0.04006836018966988, -2.1516075345208603]
    target_pose = rtde_c.moveL(pose2, VEL, ACCEL)
    current_pos = rtde_r.getActualTCPPose()[:3]

    pose3 = [0.6407279581251254, 0.026132187013502787, 0.13174284668670502, -2.1578488077978375, 0.03721006118796622, -2.1503477719171875]
    target_pose = rtde_c.moveL(pose3, VEL, ACCEL)
    current_pos = rtde_r.getActualTCPPose()[:3]
    
    pose4 = [0.34831963440789965, 0.029575520644522575, 0.1317501621068473, -2.157808711609508, 0.03712219055585839, -2.150438204785304]
    target_pose = rtde_c.moveL(pose4, VEL, ACCEL)
    current_pos = rtde_r.getActualTCPPose()[:3]

def NawaPusher():
    #Position 1. Another approach step, high above position 3
    new_pose = [0.626032384038685, -0.18281333086155396, 0.2885413248880511, -1.1663354611899008, -1.2380171806855922, -1.1716553519330546]
    target_pose = rtde_c.moveL(new_pose, VEL, ACCEL)
    current_pos = rtde_r.getActualTCPPose()[:3]
    print(current_pos)


    #Position 2. Just about to push, pusher is right above reader module.
    new_pose = [0.7563443979091746, -0.1695957000898453, 0.14223663820099358, -1.1703089341867992, -1.2408758182424429, -1.1620150762338364]
    target_pose = rtde_c.moveL(new_pose, VEL, ACCEL)
    current_pos = rtde_r.getActualTCPPose()[:3]
    print(current_pos)


    #Position 3. Pushing motion completed
    new_pose = [0.7395772307236698, 0.08323683102727122, 0.1422368774298231, -1.1702951950059732, -1.240909995007869, -1.1620928992525772]
    target_pose = rtde_c.moveL(new_pose, VEL, ACCEL)
    current_pos = rtde_r.getActualTCPPose()[:3]
    print(current_pos)

    #Back to position 2
    new_pose = [0.7563443979091746, -0.1695957000898453, 0.14223663820099358, -1.1703089341867992, -1.2408758182424429, -1.1620150762338364]
    target_pose = rtde_c.moveL(new_pose, VEL, ACCEL)
    current_pos = rtde_r.getActualTCPPose()[:3]
    print(current_pos)

    #Position 1
    new_pose = [0.626032384038685, -0.18281333086155396, 0.2885413248880511, -1.1663354611899008, -1.2380171806855922, -1.1716553519330546]
    target_pose = rtde_c.moveL(new_pose, VEL, ACCEL)
    current_pos = rtde_r.getActualTCPPose()[:3]
    print(current_pos)

def GetRobotPosition():
    return rtde_r.getActualTCPPose()[:3]

#Top Coupon

# ROBOT_IP = "192.168.1.100"
# ACCEL = 0.5  # m/s^2
# VEL = 0.05
# rtde_c = RTDEControl(ROBOT_IP)
# rtde_r = RTDEReceive(ROBOT_IP)
# current_pos = rtde_r.getActualTCPPose()[:3]
# print(current_pos)
# new_pose = [0.449517148586388, 0.18645957568745108, 0.16684860829051368, 1.948, -2.139, -0.252]
# target_pose = rtde_c.moveL(new_pose, VEL, ACCEL)
# current_pos = rtde_r.getActualTCPPose()[:3]
# print(current_pos)