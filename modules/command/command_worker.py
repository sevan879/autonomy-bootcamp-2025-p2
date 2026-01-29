"""
Command worker to make decisions based on Telemetry Data.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import command
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def command_worker(
    connection: mavutil.mavfile,
    target: command.Position,
    input_queue: queue_proxy_wrapper.QueueProxyWrapper,  # TelemetryData in
    output_queue: queue_proxy_wrapper.QueueProxyWrapper,
    controller: worker_controller.WorkerController,
) -> None:
    """
    Worker process.

    args... describe what the arguments are
    """
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (command.Command)
    result, command_instance = command.Command.create(
        connection,
        target,
        local_logger,
    )

    if not result:
        local_logger.error("Failed to create Command", True)
        return
    # Main loop: do work.
    assert command_instance is not None

    while not controller.is_exit_requested():
        controller.check_pause()
        try:
            if input_queue.queue.empty():
                continue
            telemetry_data = input_queue.queue.get(timeout=1.0)
        except Exception as e:
            local_logger.error(f"Get input queue error: {e}", True)
            continue

        try:
            # Process telemetry data to get command
            result, command_data = command_instance.run(telemetry_data)

            if not result:
                continue

            if command_data is not None:
                local_logger.info(f"Generated command: {command_data}", True)
                output_queue.queue.put(command_data)
        except Exception as e:
            local_logger.error(f"Command processing error: {e}", True)
            continue

        time.sleep(0.5)
        


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
