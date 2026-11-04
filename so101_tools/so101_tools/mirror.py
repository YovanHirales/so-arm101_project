#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from vassar_feetech_servo_sdk import ServoController

class Mirror(Node):

    def __init__(self):
        super().__init__('mirror')
        
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        self.i = 0
        
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        # Initialize controller with your servo configuration
        self.servo_ids = [1, 2, 3, 4, 5, 6]
        self.controller = ServoController(servo_ids=self.servo_ids, servo_type="sts")
        self.controller.connect()

    def timer_callback(self):
        # Read all configured servos
        positions = self.controller.read_all_positions()
        for motor_id, pos in positions.items():
            self.get_logger().info(f"Motor {motor_id}: {pos} ({pos/4095*100:.1f}%)")
        
        msg = String()
        msg.data = f'Hello World: {self.i}'
        self.i += 1
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    mirror = Mirror()

    rclpy.spin(mirror)

    mirror.destroy_node()
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
