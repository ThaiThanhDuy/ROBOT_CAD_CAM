#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import json
import transforms3d.euler
from geometry_msgs.msg import Pose
from moveit_commander import MoveGroupCommander, RobotCommander, PlanningSceneInterface
import moveit_commander


class JSONPathExecutor(Node):
    def __init__(self):
        super().__init__('json_path_executor')

        # ===== Khởi tạo MoveIt2 =====
        moveit_commander.roscpp_initialize([])
        self.robot = RobotCommander()
        self.scene = PlanningSceneInterface()
        self.group_name = 'panda_arm'
        self.move_group = MoveGroupCommander(self.group_name)

        # ===== Cấu hình =====
        self.toolpath = self.load_json_path('/home/duy/code/ROBOT_CAD_CAM/tcp_path.json')  # ← THAY đường dẫn JSON tại đây

        # ===== Thực thi =====
        self.execute_path()

    def load_json_path(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data

    def euler_to_quaternion(self, rx, ry, rz):
        # transforms3d trả về (w, x, y, z)
        q = transforms3d.euler.euler2quat(rx, ry, rz)
        return q[1], q[2], q[3], q[0]  # Chuyển về (x, y, z, w)

    def execute_path(self):
        waypoints = []

        for point in self.toolpath:
            pose = Pose()
            # Đổi đơn vị từ mm → mét nếu cần
            pose.position.x = point['x'] / 1000.0
            pose.position.y = point['y'] / 1000.0
            pose.position.z = point['z'] / 1000.0

            qx, qy, qz, qw = self.euler_to_quaternion(point['rx'], point['ry'], point['rz'])
            pose.orientation.x = qx
            pose.orientation.y = qy
            pose.orientation.z = qz
            pose.orientation.w = qw

            waypoints.append(pose)

        # ===== Lập kế hoạch Cartesian path =====
        (plan, fraction) = self.move_group.compute_cartesian_path(
            waypoints,
            eef_step=0.01,
            jump_threshold=0.0
        )

        self.get_logger().info(f'✅ Lập kế hoạch thành công: {fraction*100:.2f}%')
        if fraction > 0.9:
            self.move_group.execute(plan, wait=True)
        else:
            self.get_logger().warn("⚠️ Kế hoạch không đủ chính xác, không thực thi.")


def main(args=None):
    rclpy.init(args=args)
    node = JSONPathExecutor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
