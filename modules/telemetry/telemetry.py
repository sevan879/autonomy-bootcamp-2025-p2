"""
Telemetry gathering logic.
"""

import time

from pymavlink import mavutil

from ..common.modules.logger import logger


class TelemetryData:  # pylint: disable=too-many-instance-attributes
    """
    Python struct to represent Telemtry Data. Contains the most recent attitude and position reading.
    """

    def __init__(
        self,
        time_since_boot: int | None = None,  # ms
        x: float | None = None,  # m
        y: float | None = None,  # m
        z: float | None = None,  # m
        x_velocity: float | None = None,  # m/s
        y_velocity: float | None = None,  # m/s
        z_velocity: float | None = None,  # m/s
        roll: float | None = None,  # rad
        pitch: float | None = None,  # rad
        yaw: float | None = None,  # rad
        roll_speed: float | None = None,  # rad/s
        pitch_speed: float | None = None,  # rad/s
        yaw_speed: float | None = None,  # rad/s
    ) -> None:
        self.time_since_boot = time_since_boot
        self.x = x
        self.y = y
        self.z = z
        self.x_velocity = x_velocity
        self.y_velocity = y_velocity
        self.z_velocity = z_velocity
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw
        self.roll_speed = roll_speed
        self.pitch_speed = pitch_speed
        self.yaw_speed = yaw_speed

    def __str__(self) -> str:
        return f"""{{
            time_since_boot: {self.time_since_boot},
            x: {self.x},
            y: {self.y},
            z: {self.z},
            x_velocity: {self.x_velocity},
            y_velocity: {self.y_velocity},
            z_velocity: {self.z_velocity},
            roll: {self.roll},
            pitch: {self.pitch},
            yaw: {self.yaw},
            roll_speed: {self.roll_speed},
            pitch_speed: {self.pitch_speed},
            yaw_speed: {self.yaw_speed}
        }}"""


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class Telemetry:
    """
    Telemetry class to read position and attitude (orientation).
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
        telemetry_period: float,  # seconds
    ):
        instance = None
        try:
            instance = Telemetry(
            key=cls.__private_key,
            connection=connection,
            local_logger=local_logger,
            telemetry_period=telemetry_period,)
        except Exception as e: 
            local_logger.error(f"Exception raised while creating Telemetry: {e}", True)
            return False, None
        return True, instance

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
        telemetry_period: float,  # seconds
    ) -> None:
        assert key is Telemetry.__private_key, "Use create() method"

        # Do any intializiation here

        self._connection = connection
        self._local_logger = local_logger
        self._telemetry_period = telemetry_period

    def run(
        self,
    ):
        """
        Receive LOCAL_POSITION_NED and ATTITUDE messages from the drone,
        combining them together to form a single TelemetryData object.
        """



        # Read MAVLink message LOCAL_POSITION_NED (32)
        # Read MAVLink message ATTITUDE (30)
        # Return the most recent of both, and use the most recent message's timestamp
        start_time = time.time()
        attitude_msg = None
        position_msg = None
        most_recent_timestamp = 0

        while (time.time() - start_time) < self._telemetry_period:
            try:
                msg = self._connection.recv_match(
                    type=["LOCAL_POSITION_NED", "ATTITUDE"],
                    blocking=False,
                )
                if msg is None:
                    continue

                if msg.get_type() == "LOCAL_POSITION_NED":
                    position_msg = msg
                    most_recent_timestamp = msg.time_boot_ms
                elif msg.get_type() == "ATTITUDE":
                    attitude_msg = msg
                    most_recent_timestamp = msg.time_boot_ms
            except Exception as e:
                self._local_logger.error(f"Failed to receive MAVLink message: {e}", True)
                return False, None
        telemetry_data = TelemetryData()
        telemetry_data.time_since_boot = most_recent_timestamp
        if position_msg is not None:
            telemetry_data.x = position_msg.x
            telemetry_data.y = position_msg.y
            telemetry_data.z = position_msg.z
            telemetry_data.x_velocity = position_msg.vx
            telemetry_data.y_velocity = position_msg.vy
            telemetry_data.z_velocity = position_msg.vz
        if attitude_msg is not None:
            telemetry_data.roll = attitude_msg.roll
            telemetry_data.pitch = attitude_msg.pitch
            telemetry_data.yaw = attitude_msg.yaw
            telemetry_data.roll_speed = attitude_msg.rollspeed
            telemetry_data.pitch_speed = attitude_msg.pitchspeed
            telemetry_data.yaw_speed = attitude_msg.yawspeed
        return True, telemetry_data
    


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
