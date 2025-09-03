# Automaton
Automate any task on Linux with computer vision

> **au·tom·a·ton  (ô-tŏmʻə-tŏn′, -tən)**  
> *noun*  
> A machine or mechanism that operates without human intervention, especially a robot.

Let's say you need a _complex computer task_ to be done so many times that no human would willingly sit down and do it by hand.
- Every day, check a list of tracking numbers and fill out complaint forms for missing packages.
- Every hour, check a youtube channel for new videos and download any new ones found.
- Every minute, refresh a website to track the number of views/likes/comments to a spreadsheet.
- Every 10 seconds, check the value of a currency/crypto/stock and log it to a file.

How will you automate it? Most people would try to approach it 1 of 2 ways:

1. Build a custom program, use APIs (assuming they exist), might involve reverse-engineering websites or programs.
   - Reliability: **HIGH**
   - Difficulty: **HIGH**
   - Development time: **HIGH**
2. Make a shell script that blindly repeats human actions (move the mouse to preset coordinates, wait 2 seconds, click, repeat)
   - Reliability: **LOW**
   - Difficulty: **LOW**
   - Development time: **MEDIUM** (needs continual monitoring and maintenance)

3. Automaton offers a third option: **localized computer vision**. With it, any shell script can "see" the screen and perform tasks using the mouse and keyboard.
   - Reliability: **HIGH**
   - Difficulty: **LOW**
   - Development time: **LOW**

### Computer vision? Doesn't that require a cloud API service, or a powerful graphics card?
- **Nope.**
### Doesn't computer vision require good programming skills?
- **Not anymore.** ( ͡° ͜ʖ ͡°)

In fact, OpenCV's vision algorithm is so lightweight, that even with it running locally on a Raspberry Pi's CPU power alone, it still finds and clicks buttons on the screen quicker than any human can.  
Automaton is here to help give this power to anybody, even beginners.
- Use the full suite of desktop automation functions, all of which work in both X11 and Wayland.
- Show it regions of the screen to look for, then tell it how to interact with those regions.
- Blaze through capturing screen regions and coordinates, thanks to a custom photo editor.
- And use the ChatGPT template to get guided scripting assistance.

## Get started:
```
git clone https://github.com/Botspot/automaton
./automaton/gui
```
## Supported platforms:

- Any Debian flavored Linux distro with a X11 or wlroots Wayland compositor (x86_64, or arm64)
- Headless/server usage is supported. Just use an invisible subscreen to run everything inside a headless isolated graphics environment.
- For Wayland compositors not based on wlroots, such as GNOME: Use a subscreen. The functions for simulating the mouse and keyboard would need to be expanded to use a new tool in these environments. (open an issue if you can help with that)
- This should still work on non-Debian distros, but the script will ask you to install needed dependencies manually.

## Usage:
In simple terms, Automaton provides you with a variety of bash functions in the `api` script. These functions run just like normal linux commands, and can work together in a script to do just about anything.  
However, you don't need to be experienced with shell scripting to use this!! For basic automation tasks, the code basically writes itself.

Since nobody enjoys reading documentation, I'm trying a new approach: **the graphical interface *is* the documentation.**  
![screenshot](https://github.com/user-attachments/assets/bfb2dfea-9fb3-42b0-8dec-8b45ab450ca0)  
These buttons help generate premade chunks of working code. Simply click one, adjust any options it may have, then paste the code chunk into your script.  
![screenshot](https://github.com/user-attachments/assets/673de504-ce40-4c9a-9c5e-4c205cc96b9a)  
In this example, here's the code that was generated from those options:  
![screenshot](https://github.com/user-attachments/assets/1887e1a2-a256-475c-8877-216e13c42463)

## Status:
This project is in BETA. It should be in working order, but it's also very new. (Released on August 30, 2025)  
Was this useful to you? Please give feedback!!! So far not one person has even reported to me that they have even tried it yet. :(  
[Report bugs here](https://github.com/Botspot/automaton/issues). [Ask questions](https://github.com/Botspot/automaton/issues). [Join the discord server](https://discord.gg/RXSTvaUvuu).
