# NARS-FighterPlane (Windows)
NARS-FighterPlane is a game in which NARS serves as an AI 
controlling a fighter plane to hit enemy planes.

# Preparation
1. Install Python 3 (my python version is 3.8) and pygame package. To use python in the command window, it should be added to the PATH system environment variable like "C:\Python\Python38-32\".
2. To launch ONA, cygwin should be installed and added to the PATH variable like "C:\cygwin64\bin".
3. To launch OpenNARS, Java should be installed and added to the PATH variable like "C:\Program Files\Java\jdk-14.0.2\bin".

# Launch
Open the command window under the directory of NARS-FighterPlane_v1.0 or NARS-FighterPlane_v2.0 and type `python plane_game.py opennars` or `python plane_game.py ONA`.

# v1.0 vs v2.0
The only difference between v1.0 and v2.0 lies in how the firing operation is handled: in v2.0, firing is controlled by the NARS agent, whereas in v1.0, it is managed by the game itself at a fixed rate. v1.0 is more reliable and more likely for NARS to learn and play successfully, while v2.0 remains experimental. Recommend using v1.0 for a more stable experience.


# References
OpenNARS: https://github.com/opennars/opennars

ONA: https://github.com/opennars/OpenNARS-for-Applications

NARS-Pong in Unity3D: https://github.com/ccrock4t/NARS-Pong

## Some tests
![NARS-Fighter v2 gif](https://github.com/Noctis-Xu/images/blob/main/NARS-FighterPlane_v2.0.gif)
![NARS-Fighter v2 png](https://github.com/Noctis-Xu/images/blob/main/NARS-FighterPlane_v2.0.png)
