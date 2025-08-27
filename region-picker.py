#This was 100% vibe-coded by Grok 3 in about 4 hours. Impressive.

import pygame
import sys
import math
from PIL import Image

class ImagePointSelector:
    def __init__(self, image_path, mode, rectangle_params=None):
        pygame.init()
        self.image = Image.open(image_path)
        self.original_width, self.original_height = self.image.size

        # Set fullscreen mode
        self.window_width = pygame.display.Info().current_w
        self.window_height = pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.FULLSCREEN)
        pygame.display.set_caption("Image Point Selector")

        # Load image into Pygame surface
        self.original_image = pygame.image.load(image_path).convert()

        # Mode: 'pixel', 'rectangle', or 'pixel_in_rectangle'
        self.mode = mode.lower()
        if self.mode not in ['pixel', 'rectangle', 'pixel_in_rectangle']:
            raise ValueError("Mode must be 'pixel', 'rectangle', or 'pixel_in_rectangle'")

        # Parse rectangle parameters for pixel_in_rectangle mode
        self.rect_x = None
        self.rect_y = None
        self.rect_width = None
        self.rect_height = None
        if self.mode == 'pixel_in_rectangle':
            if not rectangle_params:
                raise ValueError("pixel_in_rectangle mode requires rectangle parameters 'x,y +w+h'")
            try:
                parts = rectangle_params.replace(' ', '').split('+')
                x_y = parts[0].split(',')
                self.rect_x = int(x_y[0])
                self.rect_y = int(x_y[1])
                self.rect_width = int(parts[1])
                self.rect_height = int(parts[2])
                if (self.rect_x < 0 or self.rect_y < 0 or self.rect_width <= 0 or self.rect_height <= 0 or
                    self.rect_x + self.rect_width > self.original_width or
                    self.rect_y + self.rect_height > self.original_height):
                    raise ValueError("Invalid rectangle parameters")
            except (IndexError, ValueError):
                raise ValueError("Rectangle parameters must be in format 'x,y +w+h' with valid integers")

        # Initialize zoom levels
        self.zoom_levels = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0]
        self.zoom_index = 2  # Default 1.0 (100%)
        self.zoom_factor = self.zoom_levels[self.zoom_index]

        # Initial view position (top-left in original coords)
        self.view_x = 0.0
        self.view_y = 0.0

        # Adjust zoom and position for pixel_in_rectangle mode
        if self.mode == 'pixel_in_rectangle':
            # Find maximum zoom level where rectangle fits on screen
            max_zoom_width = self.window_width / self.rect_width
            max_zoom_height = self.window_height / self.rect_height
            max_zoom = min(max_zoom_width, max_zoom_height)
            # Select the largest zoom level that doesn't exceed max_zoom
            self.zoom_index = 0
            for i, zoom in enumerate(self.zoom_levels):
                if zoom <= max_zoom:
                    self.zoom_index = i
                else:
                    break
            self.zoom_factor = self.zoom_levels[self.zoom_index]
            # Center the rectangle
            rect_center_x = self.rect_x + self.rect_width / 2.0
            rect_center_y = self.rect_y + self.rect_height / 2.0
            self.view_x = rect_center_x - (self.window_width / self.zoom_factor) / 2.0
            self.view_y = rect_center_y - (self.window_height / self.zoom_factor) / 2.0
        else:
            # Center the image at 100% zoom for pixel and rectangle modes
            if self.original_width * self.zoom_factor < self.window_width:
                self.view_x = (self.original_width - self.window_width / self.zoom_factor) / 2.0
            if self.original_height * self.zoom_factor < self.window_height:
                self.view_y = (self.original_height - self.window_height / self.zoom_factor) / 2.0

        # Current selected pixel in original coords
        self.x = 0
        self.y = 0
        self.start_x = None  # For rectangle mode
        self.start_y = None
        self.is_dragging = False
        self.last_displayed_x = 0  # For rectangle mode output
        self.last_displayed_y = 0
        self.last_displayed_length = 0
        self.last_displayed_width = 0

        # Clock for 60 FPS
        self.clock = pygame.time.Clock()

        # Font for instructions and coordinate display
        self.font = pygame.font.SysFont("Arial", 18)

        self.run()

    def _clamp(self, val, min_val, max_val):
        return max(min_val, min(val, max_val))

    def _get_visible_width(self):
        return self.window_width / self.zoom_factor

    def _get_visible_height(self):
        return self.window_height / self.zoom_factor

    def _clamp_view(self):
        # Allow view to go beyond image bounds for edge zooming
        # No clamping to ensure black padding is possible
        pass

    def _update_scaled_image(self):
        visible_width = self._get_visible_width()
        visible_height = self._get_visible_height()

        # Crop bounds (in original image coords)
        crop_left = math.floor(self.view_x)
        crop_top = math.floor(self.view_y)
        crop_right = math.ceil(self.view_x + visible_width)
        crop_bottom = math.ceil(self.view_y + visible_height)

        # Clamp to image bounds for rendering
        render_left = max(0, crop_left)
        render_right = min(self.original_width, crop_right)
        render_top = max(0, crop_top)
        render_bottom = min(self.original_height, crop_bottom)

        if render_right <= render_left or render_bottom <= render_top:
            # No visible image area; create a blank surface
            self.scaled_surface = pygame.Surface((self.window_width, self.window_height))
            self.scaled_surface.fill((0, 0, 0))
            self.image_pos_x = 0
            self.image_pos_y = 0
            self.crop_left = crop_left
            self.crop_top = crop_top
            self.display_width = self.window_width
            self.display_height = self.window_height
            return self.scaled_surface

        # Crop the original Pygame surface
        crop_rect = pygame.Rect(render_left, render_top, render_right - render_left, render_bottom - render_top)
        cropped_surface = self.original_image.subsurface(crop_rect)

        # Calculate display position and size
        display_width = int((crop_right - crop_left) * self.zoom_factor)
        display_height = int((crop_bottom - crop_top) * self.zoom_factor)
        image_offset_x = (render_left - crop_left) * self.zoom_factor
        image_offset_y = (render_top - crop_top) * self.zoom_factor

        # Create a surface for the full visible area, filled with black
        self.scaled_surface = pygame.Surface((self.window_width, self.window_height))
        self.scaled_surface.fill((0, 0, 0))

        # Scale the cropped surface
        scaled_cropped = pygame.transform.scale(cropped_surface, (int((render_right - render_left) * self.zoom_factor), int((render_bottom - render_top) * self.zoom_factor)))

        # Blit the scaled image onto the surface at the correct offset
        self.scaled_surface.blit(scaled_cropped, (image_offset_x, image_offset_y))

        # Store crop info
        self.image_pos_x = 0  # Full surface covers the window
        self.image_pos_y = 0
        self.crop_left = crop_left
        self.crop_top = crop_top
        self.display_width = self.window_width
        self.display_height = self.window_height

        return self.scaled_surface

    def _canvas_to_original(self, canvas_x, canvas_y, apply_bounds=True):
        canvas_x = self._clamp(canvas_x, 0, self.window_width)
        canvas_y = self._clamp(canvas_y, 0, self.window_height)
        orig_x = self.crop_left + (canvas_x - self.image_pos_x) / self.zoom_factor
        orig_y = self.crop_top + (canvas_y - self.image_pos_y) / self.zoom_factor
        x = int(self._clamp(orig_x, 0, self.original_width - 1))
        y = int(self._clamp(orig_y, 0, self.original_height - 1))
        # Constrain to rectangle bounds in pixel_in_rectangle mode only for selection
        if apply_bounds and self.mode == 'pixel_in_rectangle':
            x = self._clamp(x, self.rect_x, self.rect_x + self.rect_width - 1)
            y = self._clamp(y, self.rect_y, self.rect_y + self.rect_height - 1)
        return x, y

    def _original_to_canvas(self, orig_x, orig_y):
        canvas_x = self.image_pos_x + (orig_x - self.crop_left) * self.zoom_factor
        canvas_y = self.image_pos_y + (orig_y - self.crop_top) * self.zoom_factor
        return canvas_x, canvas_y

    def run(self):
        running = True
        self._update_scaled_image()

        while running:
            # Update mouse position before processing events
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.x, self.y = self._canvas_to_original(mouse_x, mouse_y)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit(1)
                    elif event.key in [pygame.K_EQUALS, pygame.K_PLUS]:
                        if self.zoom_index < len(self.zoom_levels) - 1:
                            self._zoom_at(self.zoom_index + 1, mouse_x, mouse_y)
                    elif event.key == pygame.K_MINUS:
                        if self.zoom_index > 0:
                            self._zoom_at(self.zoom_index - 1, mouse_x, mouse_y)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.mode == 'rectangle':
                            self.start_x = self.x
                            self.start_y = self.y
                            self.is_dragging = True
                    elif event.button == 4:  # Scroll up (zoom in)
                        if self.zoom_index < len(self.zoom_levels) - 1:
                            self._zoom_at(self.zoom_index + 1, mouse_x, mouse_y)
                    elif event.button == 5:  # Scroll down (zoom out)
                        if self.zoom_index > 0:
                            self._zoom_at(self.zoom_index - 1, mouse_x, mouse_y)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if self.mode in ['pixel', 'pixel_in_rectangle']:
                            if self.mode == 'pixel_in_rectangle':
                                # Output offset from rectangle's top-left
                                offset_x = self.x - self.rect_x
                                offset_y = self.y - self.rect_y
                                print(f"+{offset_x}+{offset_y}")
                            else:
                                print(f"{self.x},{self.y}")
                            sys.stdout.flush()
                            running = False
                        elif self.mode == 'rectangle' and self.is_dragging:
                            print(f"{self.last_displayed_x},{self.last_displayed_y} "
                                  f"+{self.last_displayed_length}+{self.last_displayed_width}")
                            sys.stdout.flush()
                            running = False

            # Clear screen
            self.screen.fill((0, 0, 0))

            # Blit scaled image
            self.screen.blit(self.scaled_surface, (self.image_pos_x, self.image_pos_y))

            # Determine rectangle corners and crosshair position
            if self.mode == 'rectangle' and self.is_dragging:
                start_x, start_y = self.start_x, self.start_y
                end_x, end_y = self.x, self.y
                top_left_x = min(start_x, end_x)
                top_left_y = min(start_y, end_y)
                bottom_right_x = max(start_x, end_x) + 1  # +1 offset for rounding up
                bottom_right_y = max(start_y, end_y) + 1  # +1 offset for rounding up
                crosshair_x = top_left_x
                crosshair_y = top_left_y
                # Store last displayed coordinates for output
                self.last_displayed_x = top_left_x
                self.last_displayed_y = top_left_y
                self.last_displayed_length = abs(end_x - start_x) + 1
                self.last_displayed_width = abs(end_y - start_y) + 1
            elif self.mode == 'pixel_in_rectangle':
                top_left_x = self.rect_x
                top_left_y = self.rect_y
                bottom_right_x = self.rect_x + self.rect_width
                bottom_right_y = self.rect_y + self.rect_height
                crosshair_x = self.x
                crosshair_y = self.y
            else:
                top_left_x = self.x
                top_left_y = self.y
                bottom_right_x = min(self.x + 1, self.original_width)
                bottom_right_y = min(self.y + 1, self.original_height)
                crosshair_x = self.x
                crosshair_y = self.y

            # Draw rectangles, clamping to screen boundaries
            if (self.mode == 'pixel' and self.zoom_factor >= 4.0) or self.mode in ['rectangle', 'pixel_in_rectangle']:
                tl_canvas_x, tl_canvas_y = self._original_to_canvas(top_left_x, top_left_y)
                br_canvas_x, br_canvas_y = self._original_to_canvas(bottom_right_x, bottom_right_y)

                # Clamp rectangle coordinates to screen boundaries
                tl_canvas_x = self._clamp(tl_canvas_x, self.image_pos_x, self.image_pos_x + self.display_width)
                tl_canvas_y = self._clamp(tl_canvas_y, self.image_pos_y, self.image_pos_y + self.display_height)
                br_canvas_x = self._clamp(br_canvas_x, self.image_pos_x, self.image_pos_x + self.display_width)
                br_canvas_y = self._clamp(br_canvas_y, self.image_pos_y, self.image_pos_y + self.display_height)

                # Ensure rectangle has non-zero size
                rect_width = max(1, (br_canvas_x - tl_canvas_x))
                rect_height = max(1, (br_canvas_y - tl_canvas_y))

                # Black outer rectangle (1px larger on each side)
                black_rect = pygame.Rect(tl_canvas_x - 1, tl_canvas_y - 1, rect_width + 2, rect_height + 2)
                pygame.draw.rect(self.screen, (0, 0, 0), black_rect, 1)
                # White inner rectangle
                white_rect = pygame.Rect(tl_canvas_x, tl_canvas_y, rect_width, rect_height)
                pygame.draw.rect(self.screen, (255, 255, 255), white_rect, 1)

            # Draw top-left crosshairs
            canvas_x, canvas_y = self._original_to_canvas(crosshair_x, crosshair_y)

            if self.image_pos_y <= canvas_y <= self.image_pos_y + self.display_height:
                h_start_x = max(0, self.image_pos_x)
                h_end_x = min(self.window_width, self.image_pos_x + self.display_width)
                pygame.draw.line(self.screen, (0, 0, 0), (h_start_x, canvas_y), (h_end_x, canvas_y), 1)
                pygame.draw.line(self.screen, (255, 255, 255), (h_start_x, canvas_y - 1), (h_end_x, canvas_y - 1), 1)

            if self.image_pos_x <= canvas_x <= self.image_pos_x + self.display_width:
                v_start_y = max(0, self.image_pos_y)
                v_end_y = min(self.window_height, self.image_pos_y + self.display_height)
                pygame.draw.line(self.screen, (0, 0, 0), (canvas_x, v_start_y), (canvas_x, v_end_y), 1)
                pygame.draw.line(self.screen, (255, 255, 255), (canvas_x - 1, v_start_y), (canvas_x - 1, v_end_y), 1)

            # Render instructions and coordinate text
            instructions_text = self.font.render(
                "Click to select a pixel, scroll or +/- to zoom" if self.mode in ['pixel', 'pixel_in_rectangle'] else
                "Click and drag to select a rectangle, scroll or +/- to zoom", True, (255, 255, 255), (0, 0, 0))
            coord_text = self.font.render(
                f"{self.x},{self.y}" if self.mode == 'pixel' else
                f"+{self.x - self.rect_x}+{self.y - self.rect_y}" if self.mode == 'pixel_in_rectangle' else
                f"{self.last_displayed_x if self.is_dragging else self.x},"
                f"{self.last_displayed_y if self.is_dragging else self.y} "
                f"+{self.last_displayed_length if self.is_dragging else 1}+"
                f"{self.last_displayed_width if self.is_dragging else 1}",
                True, (255, 255, 255), (0, 0, 0))
            instructions_rect = instructions_text.get_rect()
            coord_rect = coord_text.get_rect()

            if mouse_x < self.window_width // 2:
                # Mouse on left half, text in top-right
                instructions_rect.topright = (self.window_width - 10, 10)
                coord_rect.topright = (self.window_width - 10, 10 + instructions_rect.height + 5)
            else:
                # Mouse on right half, text in top-left
                instructions_rect.topleft = (10, 10)
                coord_rect.topleft = (10, 10 + instructions_rect.height + 5)

            self.screen.blit(instructions_text, instructions_rect)
            self.screen.blit(coord_text, coord_rect)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

    def _zoom_at(self, new_zoom_index, mouse_x, mouse_y):
        # Do not apply rectangle bounds for zooming
        mouse_orig_x, mouse_orig_y = self._canvas_to_original(mouse_x, mouse_y, apply_bounds=False)

        self.zoom_index = new_zoom_index
        self.zoom_factor = self.zoom_levels[self.zoom_index]

        self.view_x = mouse_orig_x - (mouse_x - self.image_pos_x) / self.zoom_factor
        self.view_y = mouse_orig_y - (mouse_y - self.image_pos_y) / self.zoom_factor
        # No clamping here to allow black padding

        self._update_scaled_image()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please specify path to PNG image and mode: 'pixel', 'rectangle', or 'pixel_in_rectangle'")
        sys.exit(1)
    image_path = sys.argv[1]
    mode = sys.argv[2]
    rectangle_params = None
    if mode == 'pixel_in_rectangle' and len(sys.argv) < 4:
        print("pixel_in_rectangle requires a rectangular region as a third argument.")
        sys.exit(1)
    elif mode == 'pixel_in_rectangle':
        rectangle_params = sys.argv[3]
    app = ImagePointSelector(image_path, mode, rectangle_params)
