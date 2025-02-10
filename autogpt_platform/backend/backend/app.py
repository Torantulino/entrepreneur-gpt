from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.util.process import AppProcess


def run_processes(*processes: "AppProcess", **kwargs):
    """
    Execute all processes in the app. The last process is run in the foreground.
    """
    try:
        for process in processes[:-1]:
            process.start(background=True, **kwargs)

        # Run the last process in the foreground
        processes[-1].start(background=False, **kwargs)
    finally:
        for process in processes:
            process.stop()


def main(**kwargs):
    """
    Run all the processes required for the AutoGPT-server (REST and WebSocket APIs).
    """

    from backend.executor import DatabaseManager, ExecutionManager, ExecutionScheduler
    from backend.notifications import NotificationManager
    from backend.server.rest_api import AgentServer
    from backend.server.ws_api import WebsocketServer

    run_processes(
        DatabaseManager(),
        ExecutionManager(),
        ExecutionScheduler(),
        NotificationManager(),
        WebsocketServer(),
        AgentServer(),
        **kwargs,
    )


if __name__ == "__main__":
    main()
