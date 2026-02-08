"""
Decision-making logic.
"""

import math

from pymavlink import mavutil

from ..common.modules.logger import logger
from ..telemetry import telemetry


class Position:
    """
    3D vector struct.
    """

    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Command:  # pylint: disable=too-many-instance-attributes
    """
    Command class to make a decision based on recieved telemetry,
    and send out commands based upon the data.
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> "tuple[True, Command] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a Command object.
        """
        try:
            obj = cls(cls.__private_key, connection, target, local_logger)
        except Exception as e:  # pylint: disable=broad-exception-caught
            local_logger.error(f"Failed to create Command: {e}", True)
            return False, None
        return True, obj

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        target: Position,
        local_logger: logger.Logger,
    ) -> None:
        assert key is Command.__private_key, "Use create() method"

        self._vel_x = 0.0
        self._vel_y = 0.0
        self._vel_z = 0.0
        self._vectors = 0
        self._connection = connection
        self._target = target
        self._logger = local_logger

    def run(self, telemetry_data: telemetry.TelemetryData) -> "tuple[bool, str | None]":
        """
        Make a decision based on received telemetry data.
        """

        if (
            telemetry_data.x_velocity is None
            or telemetry_data.y_velocity is None
            or telemetry_data.z_velocity is None
        ):
            self.__logger.error("Telemetry missing velocity data", True)
            return False, None

        # Log average velocity for this trip so far
        self._vel_x += telemetry_data.x_velocity
        self._vel_y += telemetry_data.y_velocity
        self._vel_z += telemetry_data.z_velocity
        self._vectors += 1

        avg_vel_x = self._vel_x / self._vectors
        avg_vel_y = self._vel_y / self._vectors
        avg_vel_z = self._vel_z / self._vectors

        self._logger.info(
            f"Average Velocity - X: {avg_vel_x:.2f}, Y: {avg_vel_y:.2f}, Z: {avg_vel_z:.2f}", True
        )
        # Calculate distance to target

        if telemetry_data.z is None:
            self.__logger.error("Missing altitude data", True)
            return False, None

        delta_z = self._target.z - telemetry_data.z
        if abs(delta_z) > 0.5:
            try:
                self._connection.mav.command_long_send(
                    1,
                    0,
                    mavutil.mavlink.MAV_CMD_CONDITION_CHANGE_ALT,
                    0,
                    1,  # Altitude change rate (m/s)
                    0,
                    0,
                    0,
                    0,
                    0,
                    self._target.z,  # Target altitude
                )
            except (AttributeError, EOFError) as e:
                self._logger.error(f"Failed to send altitude command: {e}", True)
                return False, None

            return True, f"CHANGE_ALTITUDE: {delta_z}"

        # Use COMMAND_LONG (76) message, assume the target_system=1 and target_componenet=0
        # The appropriate commands to use are instructed below

        # Adjust height using the comand MAV_CMD_CONDITION_CHANGE_ALT (113)
        # String to return to main: "CHANGE_ALTITUDE: {amount you changed it by, delta height in meters}"

        # Adjust direction (yaw) using MAV_CMD_CONDITION_YAW (115). Must use relative angle to current state
        # String to return to main: "CHANGING_YAW: {degree you changed it by in range [-180, 180]}"
        # Positive angle is counter-clockwise as in a right handed system
        if telemetry_data.x is None or telemetry_data.y is None or telemetry_data.yaw is None:
            self.__logger.error("Telemetry missing position or yaw data", True)
            return False, None

        delta_x = self._target.x - telemetry_data.x
        delta_y = self._target.y - telemetry_data.y

        desired_yaw = math.degrees(math.atan2(delta_y, delta_x))

        yaw_diff = math.degrees(
            math.atan2(
                math.sin(desired_yaw - telemetry_data.yaw),
                math.cos(desired_yaw - telemetry_data.yaw),
            )
        )

        if abs(yaw_diff) > 5:
            try:
                self._connection.mav.command_long_send(
                    1,
                    0,
                    mavutil.mavlink.MAV_CMD_CONDITION_YAW,
                    0,
                    yaw_diff,  # Yaw change in degrees
                    5.0,
                    0,
                    1,
                    0,
                    0,
                    0,
                )
            except (AttributeError, EOFError) as e:
                self._logger.error(f"Failed to send yaw command: {e}", True)
                return False, None

            return True, f"CHANGING_YAW: {yaw_diff}"

        return True, "NO ACTION"


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
