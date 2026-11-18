# MC-Stronghold-Finder
This Python script calculates an estimated position of the stronghold using two Eyes of Ender.

<br>

$\color{red}{\text{[Still in development]}}$

<br>

$\color{orange}{\text{Currently unknown if such a script is legal for real runs.}}$

# How it works
It uses the player's position and facing direction for each thrown Eye of Ender.

<br>

Through simple trilateration, it calculates a position estimate of the stronghold's chunk.

<br>

*The script uses player data:*
- Player facing direction
- Player coordinates

# What you need
The script currently uses the *MCSTP* mod to gain access to player data.

# How to use it
Start the script when ready to search for the stronghold. Then:

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

After this, it waits for further runs. (Just throw the new first eye again.)

# Next fixes
- Probably add a measurement-starting shortcut like `Shift+F8` to avoid accidentally starting measurements again.
- Maybe add additional eyes to the calculation to improve accuracy.