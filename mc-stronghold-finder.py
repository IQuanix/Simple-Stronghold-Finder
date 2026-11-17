import ctypes
import json
import time

import numpy as np
import websocket

print("DEBUG: Getting Ready..")

try:
    ws = websocket.create_connection("ws://localhost:8765/mcctp")

    was_pressed = False
    state = 0

    coords_A = np.array([0, 0])
    coords_B = np.array([0, 0])
    angle_A = 0
    angle_B = 0

    while True:
        # get data
        data = json.loads(ws.recv())

        if data.get("type") == "game_state":
            # get player data
            player_state = data["playerState"]

            # check if right-clicking
            pressed = bool(ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000)

            # state-machine
            if state == 0 and pressed and not was_pressed:
                print("1. eye thrown")
                state = 1

            elif state == 1 and pressed and not was_pressed:
                print("1. position marked")
                # save second pos & angle
                coords_A = np.array([player_state["x"], player_state["z"]])  # X, Z
                angle_A = player_state["yaw"]
                state = 2

            elif state == 2 and pressed and not was_pressed:
                print("2. eye thrown")
                state = 3

            elif state == 3 and pressed and not was_pressed:
                print("2. position marked")
                # save second pos & angle
                coords_B = np.array([player_state["x"], player_state["z"]])  # X, Z
                angle_B = player_state["yaw"]
                break

            was_pressed = pressed
            time.sleep(0.01)  # debounce

    # calculate estimated position

    # headings to radians
    a = np.deg2rad(angle_A)
    b = np.deg2rad(angle_B)

    # minecraft direction vectors (X, Z)
    dir_A = np.array([-np.sin(a), np.cos(a)])
    dir_B = np.array([-np.sin(b), np.cos(b)])

    try:
        # solve for aprox. coords
        matrix = np.column_stack((dir_A, -dir_B))
        distance_A, distance_B = np.linalg.solve(matrix, coords_B - coords_A)
        stronghold = coords_A + distance_A * dir_A

        print(f"| Stronghold at:\t[{stronghold[0]:,.0f} X | {stronghold[1]:,.0f} Z]\t|")
        print(f"| Distance from here: \t» {distance_B:,.0f} blocks «\t|")
    except np.linalg.LinAlgError:  # catching error for no data
        print("DEBUG: Bad data | Prob Code Error")

except OSError:
    print("DEBUG: Connection Error | Check Minecraft MCSTP")
