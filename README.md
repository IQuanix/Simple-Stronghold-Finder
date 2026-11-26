# Simple-Stronghold-Finder (SSF)
This Python script calculates an estimated position of the stronghold using two Eyes of Ender. (MC 1.16.1)
<br>
$\color{pink}{\text{Still under development}}$
<br>

# How it works
<img width="800" height="450" alt="preGif-optimize" src="https://github.com/user-attachments/assets/e321d10e-c6d1-4740-86dc-fdf81e9909a2" />
<br>
It uses the player's position and facing direction for each thrown Eye of Ender.
<br>
Through triangulation, it calculates a positional estimate of the stronghold's chunk.
<br>

__The script uses only player data provided by the `F3 + C` debug command:__
- Player facing direction
- Player coordinates

# Is it legal for runs?
Kinda..
<br>
$\color{orange}{\text{Script not yet checked for being legal in speed running!}}$
<br>

| Feature | Status | Explanation |
|---|---|---|
| F3 + C clipboard reading | ✅ Compatible | Only uses players position and yaw from Minecraft's own debug command. |
| Stronghold triangulation | ✅ Compatible | Calculates the intersection of two manually measured directions. |
| F8 activation | ✅ Compatible | Only starts the calculator and doesn't send inputs to Minecraft. |
| Terminal interface| ✅ Compatible | Only displays information without modifying gameplay. |
| Right-click detection | ⚠️ Needs review | Automatically detects mouse input. This is only used for displaying the next step to take |
| Custom Python calculator | ⚠️ Needs review | The custom implementation is not on the official whitelist and will need to be checked |
<br>
» [Official Minecraft Speedrunning Rules](https://github.com/Minecraft-Java-Edition-Speedrunning/rules/blob/main/rules.typ) «

# What you need
The script runs on Windows and needs the Python packages from `requirements.txt`:
<br>
*(Final version will include all packages through an installer)*

<br>
For now:

```powershell
python -m pip install -r requirements.txt
```

# How to use
Check that `simple-stronghold-finder.py` and `start-simple-stronghold-finder.bat` are in the same folder. 
<br>

__Regular use:__
<br>
Execute the `start-simple-stronghold-finder.bat`, then:

- Press `F8` to start a measurement routine.
- Throw the first eye and follow it with your crosshair.
- Briefly press `F3+C` to copy your coordinates and facing direction.
- Move at least 20 blocks sideways relative to the first eye's direction. A wider baseline generally improves the estimate.
- Throw the second eye, follow it with your crosshair, and briefly press `F3+C` again.

The result panel shows the estimated X/Z position and distance from the second measurement.
<br>
Press `F8` to start another routine after a finished one. Use `Ctrl+C` in the terminal to terminate the calculator.
<br>

Note: <br>
*You can throw more then one eye without messing with the calculation. The calculator only captures the first right-click to display the next step. It only needs the clipboards content of the two `F3 + C` commands*

# Features
* Simple and light-weight terminal interface
* Calculated an estimate of the strongholds position via two eyes of ender
* Automatic clipboard content detection, so you don't need to tab out of the game
* Shows distance to estimated position from your last thrown eye
* Error handling
* Logging for later data inspection

# Accuracy
The calculator can calculate a perfect position in theory. This heavily depends on how accurate you measure the two eyes.
Examples of measurement errors:


# Next fixes/additions
- Probably add a measurement-starting shortcut like `Shift+F8` to avoid accidentally starting measurements again ✅
- Add F3+C and clipboard detection ✅
- Change or remove current coords so the calculator is fully legal for runs ✅
- ~~Maybe add additional eyes to the calculation to improve accuracy~~.
- Show a calculated position in the nether for faster traveling
