# Automaton
Automate any task on linux with computer vision

> **au·tom·a·ton  (ô-tŏmʻə-tŏn′, -tən)**  
> *noun*  
> A machine or mechanism that operates without human intervention, especially a robot.

Let's say you need a [complex computer task] to be done so many times that no human would willingly sit down and do it by hand.  
How will you automate it? Most people would try to approach it 1 of 2 ways:  
1. Build a custom program, directly talk to any APIs, may require reverse engineering website(s) or programs.
   - Reliability: **HIGH**
   - Difficulty: **HIGH**
   - Development time: **HIGH**
3. Make a shell script that blindly repeats human actions (move the mouse to preset coordinates, wait 2 seconds, click, repeat)
   - Reliability: **LOW**
   - Difficulty: **LOW**
   - Development time: **MEDIUM** (needs continual maintenance)

4. Automaton offers a third option: **localized computer vision**.
   - Reliability: **HIGH**
   - Difficulty: **LOW**
   - Development time: **LOW**

### Computer vision? Doesn't that require a cloud API service, or a powerful graphics card?
- **Nope.**
### Doesn't computer vision require good programming skills?
- **Not anymore.** ( ͡° ͜ʖ ͡°)

In fact, OpenCV's vision algorithm is so lightweight, that even with it running locally on a Raspberry Pi's CPU power alone, it still finds and clicks buttons on the screen faster than any human can.  
Automaton is here to help give this power to anybody, even beginners.
- Show it regions of the screen to look for, then tell it how to interact with those regions.
- Use the full suite of desktop automation functions, all of which work in both X11 and Wayland.
- Blaze through capturing screen regions and coordinates, thanks to a custom photo editor.
- And use the ChatGPT template to get guided scripting assistance.

## Get started:
Use any Debian flavored Linux distro. This should still work on non-debian distros, but the script will ask you to install needed dependencies manually.  
Ubuntu, Raspberry Pi OS, Pop!OS are tested to work. x86_64 and arm64 CPU architectures are tested to work.
```
git clone https://github.com/Botspot/automaton
./automaton/gui
```
## Usage:
Since nobody enjoys reading documentation, I'm trying a new approach: **the graphical interface *is* the documentation.**  
![screenshot](https://github.com/user-attachments/assets/bfb2dfea-9fb3-42b0-8dec-8b45ab450ca0)  
These buttons help generate premade chunks of working code. Simply click one, adjust any options it may have, and then paste the code chunk into your script.  
![screenshot](https://github.com/user-attachments/assets/673de504-ce40-4c9a-9c5e-4c205cc96b9a)  
In this example, here's the code that was generated from those options:  
![screenshot](https://github.com/user-attachments/assets/1887e1a2-a256-475c-8877-216e13c42463)

## Status:
This project is in BETA. It should be in working order, but it's also very new. (Released on August 30, 2025)  
Please report any bugs [here](https://github.com/Botspot/automaton/issues). Ask questions [here](https://github.com/Botspot/automaton/issues). Join my discord server [here](https://discord.gg/RXSTvaUvuu).
