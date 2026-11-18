import ctypes
import json

import numpy as np
import websocket
from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console(width=70, height=15)

# layout creation
layout = Layout()

layout.split_column(Layout(name="upper", ratio=3), Layout(name="lower", ratio=1))

layout["upper"].split_row(Layout(name="l1", ratio=1), Layout(name="r1", ratio=2))
layout["r1"].split_column(Layout(name="t1", ratio=1), Layout(name="t2", ratio=1))

"""
[#638f6e]
[#50FA7B]
[dim]
"""

actions = Text.from_markup(
    "[dim]1. eye thrown[/]\n\n"
    "[dim]1. position marked[/]\n\n"
    "[dim]2. eye thrown[/]\n\n"
    "[dim]2. position marked[/]"
)

layout["l1"].update(
    Panel(
        Align(actions, "left", vertical="middle"),
        border_style="blue",
        box=box.SQUARE,
        padding=(0, 2),
    )
)

coords = Text.from_markup(
    "Current coordinates:\n[bold bright_white]X: 000 | Y: 000 | Z: 000[/]",
    justify="center",
)

layout["t1"].update(
    Panel(
        Align.center(coords, vertical="middle"),
        border_style="blue",
        box=box.SQUARE,
        padding=0,
    )
)

stronghold = Text.assemble(
    ("Stronghold at: ", "bold"),
    "  [X: --- | Z: ---]\n\n",
    ("Distance from here: ", "bold"),
    (" » --- blocks «", "bright_magenta"),
    justify="center",
)

layout["t2"].update(
    Panel(
        Align.center(stronghold, vertical="middle"),
        border_style="blue",
        box=box.SQUARE,
        padding=0,
    )
)

log = Text.from_markup("[bold]Log:[/] Getting things ready..")

layout["lower"].update(
    Panel(
        Align(log, "left", vertical="middle"),
        border_style="blue",
        box=box.SQUARE,
        padding=(0, 1),
    )
)


def update_log(message):
    log.plain = ""
    log.append("Log: ", style="bold")
    log.append(message)


# websocket build
try:
    ws = websocket.create_connection("ws://localhost:8765/mcctp")

    # button handling
    rc_was_pressed: bool = False
    f8_was_pressed: bool = False
    state: int = 0  # state-machine

    # for later calculation of position
    coords_A: float = np.array([0, 0])
    coords_B: float = np.array([0, 0])
    angle_A: float = 0
    angle_B: float = 0

    # live dashboard ------------------------------------------------------------
    with Live(layout, console=console, refresh_per_second=4, screen=True):
        update_log("Ready for player data...")

        while True:
            # get data
            data = json.loads(ws.recv())

            if data.get("type") == "game_state":
                # get player data
                player_state = data["playerState"]

                # check if right-clicking
                rc_pressed = bool(ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000)
                # same for f8
                f8_pressed = bool(ctypes.windll.user32.GetAsyncKeyState(0x77) & 0x8000)

                update_log("Waiting for inputs...")

                #  update live coords
                coords.plain = ""
                coords.append_text(
                    Text.from_markup(
                        f"Current coordinates:\n[#db1fcb]X: {player_state['x']:,.0f} | Y: {player_state['y']:,.0f} | Z: {player_state['x']:,.0f}[/]"
                    )
                )

                # state-machine
                if state == 0 and rc_pressed and not rc_was_pressed:
                    # print("1. eye thrown")
                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#50FA7B]1. eye thrown[/]\n\n"
                            "[dim]1. position marked[/]\n\n"
                            "[dim]2. eye thrown[/]\n\n"
                            "[dim]2. position marked[/]"
                        )
                    )
                    state = 1

                elif state == 1 and f8_pressed and not f8_was_pressed:
                    # save second pos & angle
                    coords_A = np.array([player_state["x"], player_state["z"]])  # X, Z
                    angle_A = player_state["yaw"]
                    # print("1. position marked")
                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#638f6e]1. eye thrown[/]\n\n"
                            "[#50FA7B]1. position marked[/]\n\n"
                            "[dim]2. eye thrown[/]\n\n"
                            "[dim]2. position marked[/]"
                        )
                    )
                    state = 2

                elif state == 2 and rc_pressed and not rc_was_pressed:
                    # print("2. eye thrown")
                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#638f6e]1. eye thrown[/]\n\n"
                            "[#638f6e]1. position marked[/]\n\n"
                            "[#50FA7B]2. eye thrown[/]\n\n"
                            "[dim]2. position marked[/]"
                        )
                    )
                    state = 3

                elif state == 3 and f8_pressed and not f8_was_pressed:
                    # save second pos & angle
                    coords_B = np.array([player_state["x"], player_state["z"]])  # X, Z
                    angle_B = player_state["yaw"]
                    # print("2. position marked")
                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#638f6e]1. eye thrown[/]\n\n"
                            "[#638f6e]1. position marked[/]\n\n"
                            "[#638f6e]2. eye thrown[/]\n\n"
                            "[#50FA7B]2. position marked[/]"
                        )
                    )
                    state = 4

                elif state == 4:
                    # calculate estimated position

                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[dim]1. eye thrown[/]\n\n"
                            "[dim]1. position marked[/]\n\n"
                            "[dim]2. eye thrown[/]\n\n"
                            "[dim]2. position marked[/]"
                        )
                    )
                    # print("---" * 20)
                    # headings to radians
                    a = np.deg2rad(angle_A)
                    b = np.deg2rad(angle_B)

                    # minecraft direction vectors (X, Z)
                    dir_A = np.array([-np.sin(a), np.cos(a)])
                    dir_B = np.array([-np.sin(b), np.cos(b)])

                    try:
                        update_log("Calculating stronghold position...")

                        # solve for aprox. coords
                        matrix = np.column_stack((dir_A, -dir_B))
                        distance_A, distance_B = np.linalg.solve(
                            matrix, coords_B - coords_A
                        )
                        stronghold = coords_A + distance_A * dir_A

                        update_log("Position found!")

                        """
                        print(
                            f"| Stronghold at:\t[{stronghold[0]:,.0f} X | {stronghold[1]:,.0f} Z]\t|"
                        )"""
                        # print(f"| Distance from here: \t» {distance_B:,.0f} blocks «\t|")
                        stronghold = Text.assemble(
                            ("Stronghold at: ", "bold"),
                            (
                                f"  [X: {stronghold[0]:,.0f} | Z: {stronghold[1]:,.0f}]\n\n",
                                "#2fde5b",
                            ),
                            ("Distance from here: ", "bold"),
                            (f" » {distance_B:,.0f} blocks «", "bright_magenta"),
                            justify="center",
                        )

                        layout["t2"].update(
                            Panel(
                                Align.center(stronghold, vertical="middle"),
                                border_style="blue",
                                box=box.SQUARE,
                                padding=0,
                            )
                        )

                    except np.linalg.LinAlgError:  # catching error for no data
                        # print("DEBUG: Bad data | Prob Code Error")
                        pass

                    # print("---" * 20)
                    # print("New capture prepared..")
                    state = 0
                    # break

                rc_was_pressed = rc_pressed
                f8_was_pressed = f8_pressed


except OSError as e:
    # print("DEBUG: Connection Error | Check Minecraft MCSTP")
    console.print(f"[red]WebSocket connection error: {e}[/]")

except KeyboardInterrupt:
    console.print("[yellow]Dashboard stopped.[/]")
