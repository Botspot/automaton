#!/usr/bin/env python3
import cv2
import numpy as np
import sys

if len(sys.argv) != 2:
    print("Usage: subimage-search.py </path/to/named-pipe>")
    sys.exit(1)

def process_image_pair(full_path, template_path):
    full_img = cv2.imread(full_path, cv2.IMREAD_COLOR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if full_img is None or template is None:
        return "Error: Could not load images"

    result = cv2.matchTemplate(full_img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(f"Coordinates: {max_loc}, Similarity: {max_val}")

def main():
    pipe_path = sys.argv[1]
    print(f"Daemon started, watching pipe: {pipe_path}")
    sys.stdout.flush()

    try:
        while True:
            with open(pipe_path, 'r') as pipe:
                line = pipe.readline().strip()
                if not line:
                    continue
                try:
                    full_path, template_path = line.split('\t')
                    result = process_image_pair(full_path, template_path)
                    print(result)
                    sys.stdout.flush()
                except ValueError:
                    print("Error: Input must be two paths separated by a tab")
                    sys.stdout.flush()
    except KeyboardInterrupt:
        print("Daemon stopped")

if __name__ == "__main__":
    main()
