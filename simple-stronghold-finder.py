# ============================================================
# Project:  Simple Stronghold Finder (SSF)
# Version:  v2.0
# Author:   IQuanix
# Created:  2026
# ============================================================

import ctypes
import time

import numpy as np
import pyperclip
from rich import box
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text


# class for making sweeping/scrolling highlights on text
# kinda unnecessary but dope xD
class TitleSweep:
    def __init__(self, text, speed=10, width=5):
        self.text = text
        self.speed = speed
        self.width = width

    def __rich__(self):
        pos = (time.monotonic() * self.speed) % (
            len(self.text) + self.width * 4
        ) - self.width * 2

        animated = Text()

        for i, char in enumerate(self.text):
            intensity = max(0, 1 - abs(i - pos) / self.width)
            intensity = intensity * intensity * (3 - 2 * intensity)

            # Base #35FFB8 -> Highlight #E0FFF5
            r = int(53 + 171 * intensity)
            g = 255
            b = int(184 + 61 * intensity)

            animated.append(char, style=f"rgb({r},{g},{b})")

        return Text.assemble(
            animated,
            "\n",
            ("By: ", "bold bright_white"),
            ("IQuanix", "#9544ff"),
            justify="center",
        )


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

# some credits
# speed in fps, width in characters
coords = TitleSweep("Stronghold Finder V1", speed=10, width=3)

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


# function to get current windows clipboards content without reading minecraft memory
def get_clipboard() -> list[float] | None:
    # copy current clipboard
    clipboard = pyperclip.paste()
    # parse the copy
    stripped = clipboard.strip().split()

    if stripped[:6] == ["/execute", "in", "minecraft:overworld", "run", "tp", "@s"]:
        try:
            # -10.18 16.81 -535.17
            # keep only X, Z and yaw
            data = list(map(float, stripped[6:]))
            data = [data[i] for i in (0, 2, 3)]
            # fix weird minecraft endless yaw
            data[2] = ((data[2] + 180) % 360) - 180

            return data
        except (ValueError, IndexError):
            return None
    else:
        return None


# --------------------------------------
# main calculator logic

# keyboard and clipboard measurement loop
try:
    # button handling
    rc_was_pressed: bool = False
    f8_was_pressed: bool = False
    f3_was_pressed: bool = False
    c_was_pressed: bool = False
    combo_was_pressed = False
    state: int = 0  # state-machine

    # for later calculation of position
    coords_A: float = np.array([0, 0])
    coords_B: float = np.array([0, 0])
    angle_A: float = 0
    angle_B: float = 0

    # player coords from clipboard
    player_X: float = 0
    player_Z: float = 0
    player_Yaw: float = 0

    # live dashboard ------------------------------------------------------------
    with Live(layout, console=console, refresh_per_second=30, screen=True):
        update_log("Waiting for F8 activation", style="yellow", spinner=True)

        while True:
            # default syntax of f3 + c e.g.
            # /execute in minecraft:overworld run tp @s -10.18 79.00 16.81 -535.17 17.74

            # check if right-clicking & f8 & f3 & c
            rc_pressed = bool(
                ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000
            )  # eye thrown
            f8_pressed = bool(
                ctypes.windll.user32.GetAsyncKeyState(0x77) & 0x8000
            )  # start calculator
            f3_pressed = bool(
                ctypes.windll.user32.GetAsyncKeyState(0x72) & 0x8000
            )  # f3 menu
            c_pressed = bool(
                ctypes.windll.user32.GetAsyncKeyState(0x43) & 0x8000
            )  # for f3 combo and copy of coords
            combo_pressed = f3_pressed and c_pressed  # combo for clipboard

            # Start a new run on F8; keep the last result or error visible while idle.
            if state == 0 and f8_pressed and not f8_was_pressed:
                state = 1  # start measurement routine
                update_log(
                    "Measurement routine started! Waiting for first eye",
                    spinner=True,
                    style="green",
                )
                # mark t1 panel as active
                layout["l1"].renderable.border_style = "#16FF4C"

            # state-machine
            if state == 1 and rc_pressed and not rc_was_pressed:
                update_log("1. Eye detected")
                actions.plain = ""
                actions.append_text(
                    Text.from_markup(
                        "[#50FA7B blink]1. eye thrown[/]\n\n"
                        "[dim]1. position marked[/]\n\n"
                        "[dim]2. eye thrown[/]\n\n"
                        "[dim]2. position marked[/]"
                    )
                )
                state = 2

            elif state == 2 and combo_pressed and not combo_was_pressed:
                time.sleep(0.2)
                # unpack clipboards content
                data = get_clipboard()
                if data is not None:
                    player_X, player_Z, player_Yaw = data
                    # save first pos & angle
                    coords_A = np.array([player_X, player_Z])  # X, Z
                    angle_A = player_Yaw
                    update_log(
                        f"Saved: coords_A: {coords_A}, angle_A: {angle_A}",
                        style="yellow",
                    )
                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#638f6e]1. eye thrown[/]\n\n"
                            "[#50FA7B blink]1. position marked[/]\n\n"
                            "[dim]2. eye thrown[/]\n\n"
                            "[dim]2. position marked[/]"
                        )
                    )
                    state = 3
                else:
                    update_log("Invalid clipboard data!", style="red")

            elif state == 3 and rc_pressed and not rc_was_pressed:
                update_log("2. Eye detected")
                actions.plain = ""
                actions.append_text(
                    Text.from_markup(
                        "[#638f6e]1. eye thrown[/]\n\n"
                        "[#638f6e]1. position marked[/]\n\n"
                        "[#50FA7B blink]2. eye thrown[/]\n\n"
                        "[dim]2. position marked[/]"
                    )
                )
                state = 4

            elif state == 4 and combo_pressed and not combo_was_pressed:
                time.sleep(0.2)
                # unpack clipboards content
                data = get_clipboard()
                if data is not None:
                    player_X, player_Z, player_Yaw = data
                    # save second pos & angle
                    coords_B = np.array([player_X, player_Z])  # X, Z
                    angle_B = player_Yaw
                    update_log(
                        f"Saved: coords_B: {coords_B}, angle_B: {angle_B}",
                        style="yellow",
                    )
                    actions.plain = ""
                    actions.append_text(
                        Text.from_markup(
                            "[#638f6e]1. eye thrown[/]\n\n"
                            "[#638f6e]1. position marked[/]\n\n"
                            "[#638f6e]2. eye thrown[/]\n\n"
                            "[#50FA7B blink]2. position marked[/]"
                        )
                    )
                    state = 5
                else:
                    update_log(
                        "Invalid clipboard data! Just try f3 + c again", style="red"
                    )

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
                layout["l1"].renderable.border_style = "blue"

                # headings to radians
                a = np.deg2rad(angle_A)
                b = np.deg2rad(angle_B)

                # minecraft direction vectors (X, Z)
                dir_A = np.array([-np.sin(a), np.cos(a)])
                dir_B = np.array([-np.sin(b), np.cos(b)])

                matrix = np.column_stack((dir_A, -dir_B))

                # A narrow angle reduces accuracy but still has an intersection.
                # Reject parallel lines, including opposite-facing directions.
                angle_diff = abs((angle_A - angle_B + 180) % 360 - 180)
                crossing_angle = min(angle_diff, 180 - angle_diff)

                if abs(np.linalg.det(matrix)) < 1e-8:
                    update_log(
                        "Directions are too parallel! Move sideways and retry with F8.",
                        style="red",
                    )

                else:
                    try:
                        distance_A, distance_B = np.linalg.solve(
                            matrix, coords_B - coords_A
                        )

                        if distance_A < 0 or distance_B < 0:
                            update_log(
                                "Intersection is behind a measurement! Retry with f8.",
                                style="red",
                            )
                        else:
                            stronghold_coords = coords_A + distance_A * dir_A

                            distance = np.linalg.norm(stronghold_coords - coords_B)

                            stronghold = Text.assemble(
                                ("Stronghold at: ", "bold"),
                                (
                                    f"  [X: {stronghold_coords[0]:,.0f} | Z: {stronghold_coords[1]:,.0f}]\n\n",
                                    "blink2 #2fde5b",
                                ),
                                ("Distance from here: ", "bold"),
                                (f" » {distance:,.0f} blocks «", "bright_magenta"),
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
                            if crossing_angle < 2:
                                update_log(
                                    "Position found! (Small angle, low accuracy) Retry with f8",
                                    style="yellow",
                                )
                            else:
                                update_log(
                                    "Position found! Press F8 for a new measurement.",
                                    style="green",
                                )

                    except np.linalg.LinAlgError as e:  # catching error for no data
                        update_log(f"Solving error: {e}", style="red")

                state = 0

            # reset states
            rc_was_pressed = rc_pressed
            f8_was_pressed = f8_pressed
            f3_was_pressed = f3_pressed
            c_was_pressed = c_pressed
            combo_was_pressed = combo_pressed

            time.sleep(0.01)


except KeyboardInterrupt:
    update_log("Dashboard stopped.", style="red")
