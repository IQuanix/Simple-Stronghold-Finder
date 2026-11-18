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
from rich.spinner import Spinner
from rich.text import Text

console = Console(width=70, height=15)

# layout creation
layout = Layout()

layout.split_column(Layout(name="upper", ratio=3), Layout(name="lower", ratio=1))

layout["upper"].split_row(Layout(name="l1", ratio=1), Layout(name="r1", ratio=2))
layout["r1"].split_column(Layout(name="t1", ratio=1), Layout(name="t2", ratio=1))

# pre-fill all panels
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
        padding=(0, 0),
    )
)

coords = Text.from_markup(
    "Current coordinates:\n[bold bright_white]X: --- | Y: --- | Z: ---[/]",
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
    ("  [X: --- | Z: ---]\n\n", "dim"),
    ("Distance from here: ", "bold"),
    (" » --- blocks «", "dim"),
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
        padding=(0, 0),
    )
)


# function for updating the console log
def update_log(message, style="white", spinner=False):
    # Avoid restarting the spinner on every update
    current = (message, style, spinner)
    if getattr(update_log, "_last", None) == current:
        return

    update_log._last = current

    content = Text.assemble(("Log: ", "bold"), (message, style))

    # style for loading spinner
    if spinner:
        content = Spinner("dots", text=content, style="cyan")

    layout["lower"].update(
        Panel(
            Align(content, "left", vertical="middle"),
            border_style="blue",
            box=box.SQUARE,
            padding=(0, 0),
        )
    )


# websocket build
try:
    # connects with the MCCTP mod over default port 8765
    ws = websocket.create_connection("ws://localhost:8765/mcctp")

    # button handling
    rc_was_pressed: bool = False
    f8_was_pressed: bool = False
    shift_pressed: bool = False
    shift_was_pressed: bool = False
    combo_pressed: bool = False
    combo_was_pressed = False
    state: int = 0  # state-machine

    # for later calculation of position
    coords_A: float = np.array([0, 0])
    coords_B: float = np.array([0, 0])
    angle_A: float = 0
    angle_B: float = 0

    # live dashboard ------------------------------------------------------------
    with Live(layout, console=console, refresh_per_second=12, screen=True):
        update_log("Getting player data...", spinner=True)

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
                # same for either shift key
                shift_pressed = bool(
                    ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000
                )
                combo_pressed = shift_pressed and f8_pressed

                #  update live coords
                coords.plain = ""
                coords.append_text(
                    Text.from_markup(
                        f"Current coordinates:\n[#db1fcb]X: {player_state['x']:,.0f} | Y: {player_state['y']:,.0f} | Z: {player_state['z']:,.0f}[/]"
                    )
                )

                # state-machine
                if state == 0:
                    update_log("Waiting for shift + f8", style="yellow", spinner=True)
                elif state == 1:
                    update_log(
                        "Measurement routine started! Waiting for inputs",
                        spinner=True,
                        style="green",
                    )
                # starts a new marking run after shift+f8 combo
                if state == 0 and combo_pressed and not combo_was_pressed:
                    state = 1  # start measurement routine

                # state-machine
                if state == 1 and rc_pressed and not rc_was_pressed:
                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#50FA7B]1. eye thrown[/]\n\n"
                            "[dim]1. position marked[/]\n\n"
                            "[dim]2. eye thrown[/]\n\n"
                            "[dim]2. position marked[/]"
                        )
                    )
                    state = 2

                elif state == 2 and f8_pressed and not f8_was_pressed:
                    # save second pos & angle
                    coords_A = np.array([player_state["x"], player_state["z"]])  # X, Z
                    angle_A = player_state["yaw"]

                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#638f6e]1. eye thrown[/]\n\n"
                            "[#50FA7B]1. position marked[/]\n\n"
                            "[dim]2. eye thrown[/]\n\n"
                            "[dim]2. position marked[/]"
                        )
                    )
                    state = 3

                elif state == 3 and rc_pressed and not rc_was_pressed:
                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#638f6e]1. eye thrown[/]\n\n"
                            "[#638f6e]1. position marked[/]\n\n"
                            "[#50FA7B]2. eye thrown[/]\n\n"
                            "[dim]2. position marked[/]"
                        )
                    )
                    state = 4

                elif state == 4 and f8_pressed and not f8_was_pressed:
                    # save second pos & angle
                    coords_B = np.array([player_state["x"], player_state["z"]])  # X, Z
                    angle_B = player_state["yaw"]

                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#638f6e]1. eye thrown[/]\n\n"
                            "[#638f6e]1. position marked[/]\n\n"
                            "[#638f6e]2. eye thrown[/]\n\n"
                            "[#50FA7B]2. position marked[/]"
                        )
                    )
                    state = 5

                elif state == 5:
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

                    # headings to radians
                    a = np.deg2rad(angle_A)
                    b = np.deg2rad(angle_B)

                    # minecraft direction vectors (X, Z)
                    dir_A = np.array([-np.sin(a), np.cos(a)])
                    dir_B = np.array([-np.sin(b), np.cos(b)])

                    try:
                        update_log("Calculating stronghold position", spinner=True)

                        # solve for aprox. coords
                        matrix = np.column_stack((dir_A, -dir_B))
                        distance_A, distance_B = np.linalg.solve(
                            matrix, coords_B - coords_A
                        )
                        stronghold = coords_A + distance_A * dir_A

                        update_log("Position found!")

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

                    except np.linalg.LinAlgError as e:  # catching error for no data
                        console.print(f"[red]Solving error: {e}[/]")

                    state = 0

                # reset states
                rc_was_pressed = rc_pressed
                f8_was_pressed = f8_pressed
                shift_was_pressed = shift_pressed
                combo_was_pressed = combo_pressed


except OSError as e:
    # print("DEBUG: Connection Error | Check Minecraft MCSTP")
    console.print(f"[red]WebSocket connection error: {e}[/]")

except KeyboardInterrupt:
    console.print("[yellow]Dashboard stopped.[/]")
