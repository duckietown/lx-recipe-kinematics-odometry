"""``Joystick``: a virtual joystick for the notebooks (it replaces the joystick of the old desktop).

    from lx_ros2_tools.session import RosSession
    from lx_kinematics_tools import Joystick

    ros = RosSession("myrobot")
    Joystick(ros)                        # buttons: forward / backward / turn / spin / stop
    Joystick(ros, topic="car_cmd")       # older robot images (kinematics_node listening on /ROBOT/car_cmd)

While a direction is active, a ``duckietown_msgs/Twist2DStamped`` car command (``v`` [m/s], ``omega`` [rad/s])
is published at ``rate_hz`` on ``topic`` (relative to the robot namespace, default ``car_cmd_switch_node/cmd``),
which the ``kinematics_node`` of the ROS 2 stack turns into wheel commands. ``stop`` publishes a zero command.
If the robot does not move, check which topic its kinematics node subscribes to with
``ros2 node info /ROBOT/kinematics_node`` and pass it as ``topic``.
"""
import threading
import time

import ipywidgets as W
from IPython.display import display


class Joystick:
    def __init__(self, ros, topic: str = "car_cmd_switch_node/cmd", v: float = 0.2, omega: float = 2.0, rate_hz: float = 10.0):
        from duckietown_msgs.msg import Twist2DStamped

        self.ros, self.topic, self._msg_type = ros, topic, Twist2DStamped
        self.v, self.omega = float(v), float(omega)
        self._cmd = (0.0, 0.0)
        self._active = False
        self._closed = False
        self._period = 1.0 / max(float(rate_hz), 0.1)
        self.status = W.HTML("<span style='color:#888'>stopped</span>")

        def button(label, cmd, style=""):
            b = W.Button(description=label, button_style=style, layout=W.Layout(width="130px"))
            b.on_click(lambda _, c=cmd: self.drive(*c))
            return b

        rows = [
            W.HBox([button("↶ left", (self.v, self.omega)), button("↑ forward", (self.v, 0.0)),
                    button("↷ right", (self.v, -self.omega))]),
            W.HBox([button("↺ spin left", (0.0, self.omega)), button("↓ backward", (-self.v, 0.0)),
                    button("↻ spin right", (0.0, -self.omega))]),
            W.HBox([button("■ stop", (0.0, 0.0), "danger")]),
        ]
        self.widget = W.VBox([W.HTML(f"<b>{ros.name(topic)}</b>"), *rows, self.status])
        self._thread = threading.Thread(target=self._loop, name="lx-joystick", daemon=True)
        self._thread.start()
        display(self.widget)

    def _ipython_display_(self):
        display(self.widget)

    # --- commands -------------------------------------------------------------------------------
    def drive(self, v: float, omega: float):
        """Publish ``(v, omega)`` continuously until the next command (``(0, 0)`` stops)."""
        self._cmd = (float(v), float(omega))
        self._active = bool(v) or bool(omega)
        self._publish()
        self.status.value = (f"<span style='color:#080'>v = {v:.2f} m/s, omega = {omega:.2f} rad/s</span>"
                             if self._active else "<span style='color:#888'>stopped</span>")

    def stop(self):
        self.drive(0.0, 0.0)

    def _publish(self):
        msg = self._msg_type()
        msg.header.stamp = self.ros.node.get_clock().now().to_msg()
        msg.v, msg.omega = self._cmd
        self.ros.publish(self.topic, msg)

    def _loop(self):
        while not self._closed:
            if self._active:
                try:
                    self._publish()
                except Exception:  # noqa: BLE001 - session shut down
                    pass
            time.sleep(self._period)

    def close(self):
        self.stop()
        self._closed = True
        self.widget.close()
