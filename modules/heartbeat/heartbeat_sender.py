"""
Heartbeat sending logic.
"""

from pymavlink import mavutil
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatSender:
    """
    HeartbeatSender class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> "tuple[True, HeartbeatSender] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatSender object.
        """
        try:
            instance = HeartbeatSender(
            cls.__private_key,
            connection=connection,
            local_logger=local_logger)
        except Exception as e:
            local_logger.error(f"Exception raised while creating HeartbeatSender: {e}", True)
            return False, None
        
        return True, instance

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ):
        assert key is HeartbeatSender.__private_key, "Use create() method"

        # Do any intializiation here
        self.connection = connection
        self.local_logger = local_logger

    def run(
        self,
    ):
        """
        Attempt to send a heartbeat message.
        """
        try:
            # Send heartbeat message
            self.connection.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0,
                0,
                0,
            )
            self.local_logger.info("Heartbeat sent", True)
        except Exception as e:
            self.local_logger.error(f"Failed to send heartbeat: {e}", True)
            return False
        
        self.local_logger.info("Heartbeat sent successfully", True)
        return True


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
