"""
The command line interface for the agent server
"""

import os
import pathlib

import click
import psutil

from backend import app
from backend.util.process import AppProcess


def get_pid_path() -> pathlib.Path:
    home_dir = pathlib.Path.home()
    new_dir = home_dir / ".config" / "agpt"
    file_path = new_dir / "running.tmp"
    return file_path


def get_pid() -> int | None:
    file_path = get_pid_path()
    if not file_path.exists():
        return None

    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, "r", encoding="utf-8") as file:
        pid = file.read()
    try:
        return int(pid)
    except ValueError:
        return None


def write_pid(pid: int):
    file_path = get_pid_path()
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(str(pid))


class MainApp(AppProcess):
    def run(self):
        app.main(silent=True)


@click.group()
def main():
    """AutoGPT Server CLI Tool"""
    pass


@main.command()
def start():
    """
    Starts the server in the background and saves the PID
    """
    # Define the path for the new directory and file
    pid = get_pid()
    if pid and psutil.pid_exists(pid):
        print("Server is already running")
        exit(1)
    elif pid:
        print("PID does not exist deleting file")
        os.remove(get_pid_path())

    print("Starting server")
    pid = MainApp().start(background=True, silent=True)
    print(f"Server running in process: {pid}")

    write_pid(pid)
    print("done")
    os._exit(status=0)


@main.command()
def stop():
    """
    Stops the server
    """
    pid = get_pid()
    if not pid:
        print("Server is not running")
        return

    os.remove(get_pid_path())
    process = psutil.Process(int(pid))
    for child in process.children(recursive=True):
        child.terminate()
    process.terminate()

    print("Server Stopped")


@main.command()
def gen_encrypt_key():
    """
    Generate a new encryption key
    """
    from cryptography.fernet import Fernet

    print(Fernet.generate_key().decode())


@click.group()
def test():
    """
    Group for test commands
    """
    pass


@test.command()
@click.argument("server_address")
def reddit(server_address: str):
    """
    Create an event graph
    """
    import requests

    from backend.usecases.reddit_marketing import create_test_graph

    test_graph = create_test_graph()
    url = f"{server_address}/graphs"
    headers = {"Content-Type": "application/json"}
    data = test_graph.model_dump_json()

    response = requests.post(url, headers=headers, data=data)

    graph_id = response.json()["id"]
    print(f"Graph created with ID: {graph_id}")


@test.command()
@click.argument("server_address")
def populate_db(server_address: str):
    """
    Create an event graph
    """
    import requests

    from backend.usecases.sample import create_test_graph

    test_graph = create_test_graph()
    url = f"{server_address}/graphs"
    headers = {"Content-Type": "application/json"}
    data = test_graph.model_dump_json()

    response = requests.post(url, headers=headers, data=data)

    graph_id = response.json()["id"]

    if response.status_code == 200:
        execute_url = f"{server_address}/graphs/{response.json()['id']}/execute"
        text = "Hello, World!"
        input_data = {"input": text}
        response = requests.post(execute_url, headers=headers, json=input_data)

        schedule_url = f"{server_address}/graphs/{graph_id}/schedules"
        data = {
            "graph_id": graph_id,
            "cron": "*/5 * * * *",
            "input_data": {"input": "Hello, World!"},
        }
        response = requests.post(schedule_url, headers=headers, json=data)

    print("Database populated with: \n- graph\n- execution\n- schedule")


@test.command()
@click.argument("server_address")
def graph(server_address: str):
    """
    Create an event graph
    """
    import requests

    from backend.usecases.sample import create_test_graph

    url = f"{server_address}/graphs"
    headers = {"Content-Type": "application/json"}
    data = create_test_graph().model_dump_json()
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        print(response.json()["id"])
        execute_url = f"{server_address}/graphs/{response.json()['id']}/execute"
        text = "Hello, World!"
        input_data = {"input": text}
        response = requests.post(execute_url, headers=headers, json=input_data)

    else:
        print("Failed to send graph")
        print(f"Response: {response.text}")


@test.command()
@click.argument("graph_id")
@click.argument("content")
def execute(graph_id: str, content: dict):
    """
    Create an event graph
    """
    import requests

    headers = {"Content-Type": "application/json"}

    execute_url = f"http://0.0.0.0:8000/graphs/{graph_id}/execute"
    requests.post(execute_url, headers=headers, json=content)


@test.command()
def event():
    """
    Send an event to the running server
    """
    print("Event sent")


@test.command()
@click.argument("server_address")
@click.argument("graph_id")
@click.argument("graph_version")
def websocket(server_address: str, graph_id: str, graph_version: int):
    """
    Tests the websocket connection.
    """
    import asyncio

    import websockets.asyncio.client

    from backend.server.ws_api import ExecutionSubscription, Methods, WsMessage

    async def send_message(server_address: str):
        uri = f"ws://{server_address}"
        async with websockets.asyncio.client.connect(uri) as websocket:
            try:
                msg = WsMessage(
                    method=Methods.SUBSCRIBE,
                    data=ExecutionSubscription(
                        graph_id=graph_id, graph_version=graph_version
                    ).model_dump(),
                ).model_dump_json()
                await websocket.send(msg)
                print(f"Sending: {msg}")
                while True:
                    response = await websocket.recv()
                    print(f"Response from server: {response}")
            except InterruptedError:
                exit(0)

    asyncio.run(send_message(server_address))
    print("Testing WS")


main.add_command(test)

if __name__ == "__main__":
    main()
