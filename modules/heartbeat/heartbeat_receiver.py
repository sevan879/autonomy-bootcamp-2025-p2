"""
Heartbeat receiving logic.
"""

from pymavlink import mavutil

from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
class HeartbeatReceiver:
    """
    HeartbeatReceiver class to send a heartbeat
    """

    __private_key = object()

    @classmethod
    def create(
        cls,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ):
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        try:
            instance = HeartbeatReceiver(
                key=cls.__private_key,
                connection=connection,
                local_logger=local_logger
            )
            return True, instance
        except Exception as e:
            local_logger.log_error(f"HeartbeatReceiver creation failed: {e}")
            return False, None

    def __init__(
        self,
        key: object,
        connection: mavutil.mavfile,
        local_logger: logger.Logger,
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        self._connection = connection
        self._local_logger = local_logger
        

        # Do any initialization here

    def run(
        self,
        args,  # Put your own arguments here
    ):
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        pass


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
