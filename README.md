# MC-Stronghold-Finder
This python script calculates an estimated position of the stronghold through two eyes of ender.
<br>

$\color{red}{\text{[Still in development]}}$
<br>
$\color{orange}{\text{Currently unknown if such a script is legal for real runs.}}$

# How it works
It uses the players position and facing direction at each thrown eye of ender.
<br>
Through simple trilateration it calculates a position estimate of the strongholds chunk.

# How to use it
Start the script when ready to search for the stronghold. Then:
* throw the first eye and follow it with your crosshair.
* when sure about the eye's direction press `f8` to mark the players coordinates and facing direction.
* move at least 20 blocks roughly 90° left or right of the currently facing direction.
  * (the greater the distance to the first position, the better the accuracy of the later estimated position)
* throw the second eye and follow it with your crosshair.
* press `f8` to mark the second position


The script then gives you an estimated position of the stronghold.
<br>
After this it waits for further runs. (Just throw the new first eye again.)

# Next fix
* prob. add measurement starting shortcut like `shift+f8` to not start measurements again by accident. 