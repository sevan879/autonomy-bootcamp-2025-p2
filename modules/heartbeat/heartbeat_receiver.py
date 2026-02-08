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
        heartbeat_period: float,
        disconnect_period: int,
    ) -> "tuple[True, HeartbeatReceiver] | tuple[False, None]":
        """
        Falliable create (instantiation) method to create a HeartbeatReceiver object.
        """
        try:
            instance = HeartbeatReceiver(
                key=cls.__private_key,
                connection=connection,
                local_logger=local_logger,
                heartbeat_period=heartbeat_period,
                disconnect_period=disconnect_period,
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
        heartbeat_period: float,
        disconnect_period: int,
    ) -> None:
        assert key is HeartbeatReceiver.__private_key, "Use create() method"

        self._connection = connection
        self._local_logger = local_logger

        self.__connection = connection

        # periods in seconds or floats
        self.__heartbeat_period = heartbeat_period
        self.__disconnect_period = disconnect_period

        self.__missed = 0
        self.__dced = True

    def run(
        self,
    ) -> bool:

        print(self._local_logger)
        """
        Attempt to recieve a heartbeat message.
        If disconnected for over a threshold number of periods,
        the connection is considered disconnected.
        """
        msg = None
        try:
            msg = self.__connection.recv_match(
                type="HEARTBEAT",
                blocking=True,
                timeout=self.__heartbeat_period,
            )
        except Exception as e:
            self._local_logger.error(f"Failed to receive heartbeat: {e}", True)
            return False

        if msg is not None and msg.get_type() == "HEARTBEAT":
            self._local_logger.info("Heartbeat received", True)
            self.__missed = 0
            self.__dced = False

            if self.__dced:
                self._local_logger.info("Heartbeat connection established", True)
        else:
            self.__missed += 1
            self._local_logger.warning(f"Missed heartbeat #{self.__missed}", True)

            if self.__missed >= self.__disconnect_period:
                if not self.__dced:
                    self._local_logger.error("Heartbeat connection lost", True)
                self.__dced = True

        if self.__dced:
            return False
        return True


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
