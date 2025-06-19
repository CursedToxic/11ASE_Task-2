# 11ASE_Task-2
 
# Sahur Shooter
A really basic FPS game made with ursina engine in python. The goal is to defeat the boss at the end. This game kinda sucks (it gets boring after a while).

## Installation
Clone the repository and navigate to the project directory:
11ASE_Task-2/main/sahur_shooter.py

Then run the file after installing the dependencies in 'requirements.txt'.

Note: I tried to get a .exe file, it didn't work for me.

## Features
- Title screen with Play and Quit buttons.
- A 'You Died' screen when player dies.
- A 'You Win' screen after the player defeats the boss.
- Enemy and map textures.
- Player gun and knife texture.
- Funny animation on karambit.

## Requirements
To run this program, you need to install the following dependencies:

- `ursina` for the main window.
- `random` for random enemy spawnpoints
- `tkinter` for enemy movement towards player system (rotation and wall avoidance)
- `pillow` to display images (imported with ursina)

### Install dependencies
To install the required dependencies, you can run:

```bash
pip install -r requirements.txt