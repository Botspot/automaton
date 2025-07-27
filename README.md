# automaton
Bash-based alternative to SikuliX, this automates any task on linux with computer vision

> **au·tom·a·ton  (ô-tŏmʻə-tŏn′, -tən)**  
> *noun*  
> A machine or mechanism that operates without human intervention, especially a robot.

The goal here is to automate nearly any repetitive task on a computer - not just with a series of coordinates to click with delays in-between, but with some adaptive intelligence behind it.  

Imagine you want to download a payment report file from your bank's website. And the website is slow, and it takes a lot of clicks to do get the job done.  
I once made a little shell script that did something like:
```bash
chromium https://my.bank & # go to my bank's website
sleep 60                   # wait for page to load

click 1023,539             # click username field (hopefully it is there)
type '********'            # type the username
click 1023,589             # click password field (hopefully it is there)
type '********'            # type password
click 1023,600             # click LOGIN button (hopefully it is there)
sleep 20                   # wait for page to load

...                        # many more steps...

click 1794,378             # click download report button (hopefully it is there)
type Alt+F4                # close the browser
```
...And it stopped working in a week, because the website got updated and one of the buttons moved downwards a few pixels.  All subsequent steps had the mouse clicking in random places on the login screen.  

With Automaton, you could show it a screenshot of what to look for, and it will find it no matter where it appears on the screen. So now the script could be like:
```bash
chromium https://my.bank &        # go to my bank's website
find_and_click username-field.png # wait for username field to appear, and click it
type '********'                   # type the username
find_and_click password-field.png # find the password field, and click it
type '********'                   # type the password
find_and_click login-button.png   # wait for login button to appear, and click it

...                               # many more steps...

find_and_click download.png       # click download report button
type Alt+F4                       # close the browser
```
With a sliding window template matching algorithm from OpenCV, this is possible and practical. After just a couple hours of messing around, I've already gotten the core functionality working. Computer vision can be slow, but for finding a small object in a 1920x1080 screenshot, it takes around 0.3 seconds on my Pi5. That's plenty fast enough for my purposes.

Right now, there's just a proof of concept python script that will find the coordinates of a small image within a larger one. If you want to play around with it right now, do something like:
```bash
sudo apt install python3-opencv python3-numpy
git clone https://github.com/Botspot/automaton

#make a named pipe to send requests to the script
mkfifo /tmp/named-pipe

#start up the script (it runs forever, waiting for requests to come through the named pipe)
./automaton/subimage-search.py /tmp/named-pipe

#in another terminal:
echo -e '/home/pi/Pictures/screenshot.png\t/home/pi/Pictures/cropped.png' > /tmp/named-pipe
#provide full paths to 2 images: a full screenshot and a cropped version with your object of interest

#watch the output in the first terminal - it should respond with something like:
Coordinates: (1446, 649), Similarity: 1.0

#to clean up:
rm /tmp/named-pipe
```
I plan to add more to this repo as time goes on. The end goal is to make a step-by-step interface and a simple scripting language, allowing anybody to automate any computer task on any Linux distro. (Wayland or X11, ARM or x86)  
Please click the Star button on the repository if this interests you! (I want to get an idea of how exciting this idea is to other people)
