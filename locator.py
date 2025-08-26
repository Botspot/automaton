#!/usr/bin/env python3

#Written by Botpot with a lot of help from Grok 3

#locator.py waits for PNG image pairs to process on the $1 named pipe.
#Image pairs are separated by a tab character.
#Resulting coordinates and percent similarity is sent to the ${1}.out pipe.
#Example output: Coordinates: 118,228 Similarity: 99%
#Output is blank if similarity is below 80%.
#This script creates the pipes.
#This script exits when the input pipe is deleted.

import cv2  # Import OpenCV for image processing
import sys  # Import sys for command-line arguments and exit functionality
import os  # Import os for file and directory operations
import select

# Check if the correct number of command-line arguments is provided
if len(sys.argv) != 2:
    sys.exit(1)  # Exit if the number of arguments is not equal to 2

pipe_path = sys.argv[1]  # Get the named pipe path from command-line arguments

# Check if the named pipe already exists
if os.path.exists(pipe_path):
    os.remove(pipe_path)  # Remove the existing pipe
os.mkfifo(pipe_path)  # Create a new named pipe

output_pipe_path = pipe_path + ".out"  # Define the output pipe path
# Check if the output named pipe already exists
if os.path.exists(output_pipe_path):
    os.remove(output_pipe_path)  # Remove the existing output pipe
os.mkfifo(output_pipe_path)  # Create a new output named pipe

try:
    while True:  # Infinite loop to continuously read from the input pipe
        # Check if the input named pipe still exists
        if not os.path.exists(pipe_path):
            sys.exit(2)  # Exit with code 2 if the input pipe is removed
        
        pipe_fd = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK) # Open input pipe in non-blocking read mode
        pipe = os.fdopen(pipe_fd, 'r')
        rlist, _, _ = select.select([pipe_fd], [], [], 0.1) # Use select to check if input pipe is readable
        if pipe_fd in rlist:
            # Read input line
            line = pipe.readline().strip()  # Read a line from the pipe and strip whitespace
            try:
                # Split the line into pattern and screenshot paths
                pattern_path, screenshot_path = line.split('\t')
                # Read the full image and template image
                full_img = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
                template = cv2.imread(pattern_path, cv2.IMREAD_COLOR)
                # Check if both images are loaded successfully
                if full_img is not None and template is not None:
                    # Perform template matching
                    result = cv2.matchTemplate(full_img, template, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)  # Get the best match value and location
                    # Check if the similarity is above the threshold
                    if max_val >= 0.8:
                        x, y = max_loc  # Get the coordinates of the best match
                        # Prepare the output string with coordinates and similarity percentage
                        output = f"{x},{y} Similarity={int(max_val * 100)}%\n"
                    else:
                        output = ""  # No match found, set output an empty string
                    with open(output_pipe_path, 'w') as write_pipe:  # Open the output pipe for writing
                        write_pipe.write(output)  # Write the output to the pipe
                        write_pipe.flush()  # Flush the pipe to ensure data is sent
            except ValueError:
                #line empty or not readible: output nothing and exit
                with open(output_pipe_path, 'w') as write_pipe:  # Open the output pipe for writing
                    write_pipe.write("")  # Write no output to the pipe
                    write_pipe.flush()  # Flush the pipe to ensure data is sent
                    sys.exit(3) #Exit with error code 3
except KeyboardInterrupt:
    sys.exit(0) #exit if interrupted by keyboard
