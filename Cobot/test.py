import time
from dataclasses import dataclass
from rtde_control import RTDEControlInterface as RTDEControl
from rtde_receive import RTDEReceiveInterface as RTDEReceive
import math
import numpy as np

#Bottom Coupon

ROBOT_IP = "192.168.1.100"
ACCEL = 0.1  # m/s^2
VEL = 0.01
rtde_c = RTDEControl(ROBOT_IP)
rtde_r = RTDEReceive(ROBOT_IP)
current_pos = rtde_r.getActualTCPPose()[:6]
print(current_pos)


new_pose = [0.37882514875049006 - 0.055, 0.2617769379120669, 0.11130449137703621, 2.1582592208926252, -2.2531529674777167, 0.02475015888346646]
target_pose = rtde_c.moveL(new_pose, VEL, ACCEL)
current_pos = rtde_r.getActualTCPPose()[:3]
print(current_pos)




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