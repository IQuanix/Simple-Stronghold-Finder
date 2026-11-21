# MC-Stronghold-Finder
This Python script calculates an estimated position of the stronghold using two Eyes of Ender.

<br>

$\color{red}{\text{[Still in development]}}$

<br>

$\color{orange}{\text{Currently unknown if such a script is legal for real runs.}}$

# How it works
It uses the player's position and facing direction for each thrown Eye of Ender.

<br>

Through triangulation, it calculates a position estimate of the stronghold's chunk.

<br>

*The script uses player data:*
- Player facing direction
- Player coordinates

# What you need
Both versions run on Windows and need the Python packages in `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

V2 uses Minecraft Java Edition's `F3+C` clipboard command in the Overworld and does not need the mod connection. V1 uses the *MCSTP* mod to gain access to player data.

# How to use v2

Run `python mc-stronghold-finder-v2.py`, then:

- Press `F8` to start a measurement routine.
- Throw the first eye and follow it with your crosshair.
- Briefly press `F3+C` to copy your coordinates and facing direction.
- Move at least 20 blocks sideways relative to the first eye's direction. A wider baseline generally improves the estimate.
- Throw the second eye, follow it with your crosshair, and briefly press `F3+C` again.

The result panel shows the estimated X/Z position and distance from the second measurement. Directions less than 3 degrees apart still produce a result, with a low-accuracy warning. Parallel directions and intersections behind either measurement produce an error. The completion message or error stays visible until another action updates it. Press `F8` to start another routine; use `Ctrl+C` in the terminal to stop.

# How to use v1
Start the script when ready to search for the stronghold. Then:

- Press `Shift+F8` to start a measurement routine.
- Throw the first eye and follow it with your crosshair.
- When sure about the eye's direction, press `F8` to mark the player's coordinates and facing direction.
- Move at least 20 blocks roughly 90° left or right of the current facing direction.
  - (The greater the distance from the first position, the better the accuracy of the later estimated position.)
- Throw the second eye and follow it with your crosshair.
- Press `F8` to mark the second position.

The script then gives you an estimated position of the stronghold.
<br>
To stop use `ctrl+c` in the terminal

<br>

After this, it waits for further runs. Press `Shift+F8` to begin again.

# Development notes

Verified on 2026-11-20: v2 previously rejected every angle difference below 3 degrees, then overwrote the error with its idle message. It now solves nonparallel measurements and keeps result/error messages visible. The keyboard loop polls at roughly 100 Hz instead of spinning continuously.

Regression checks run the actual v2 loop with simulated key presses and clipboard commands, then inspect the rendered dashboard:

```powershell
python -m unittest discover -s tests -v
```

These checks cover narrow and wide angles, parallel and opposite-facing directions, backward intersections, wrapped yaw, malformed clipboard data, and starting another run after a failure. They do not verify Minecraft's real clipboard timing. V2's separate current-coordinates panel still contains placeholders; measurements are captured only on `F3+C`.

Project knowledge stays in this repository. NEXUS storage was declined on 2026-11-20; session ownership is Codex/OpenAI.

Next planned step: verify a complete two-eye run in Minecraft, including a narrow-angle result and the timing of both `F3+C` captures.

# Next fixes
- Probably add a measurement-starting shortcut like `Shift+F8` to avoid accidentally starting measurements again. ✅
- Add F3+C and clipboard detection. Implemented in v2; run eligibility remains unverified. ✅
- change or remove current coords so the calculator is fully legal for runs
- ~~Maybe add additional eyes to the calculation to improve accuracy~~.
