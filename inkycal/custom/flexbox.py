import json
import logging
import os.path
from enum import Enum

import numpy
from PIL import Image, ImageDraw, ImageFont, ImageOps

from inkycal.custom.inkycal_colours import InkycalColours
from inkycal.utils import InkycalFont

logger = logging.getLogger(__name__)


# class TextAlignment(Enum):
#     CENTER = 1
#     LEFT = 2
#     RIGHT = 3
#     TOP = 4
#     BOTTOM = 5

#
# class Flexbox:
#
#     def __init__(self, num_rows: int, num_cols: int, width: int, height: int, font_path: str,
#                  font_size: int = 1, padding: int = 10, border_radius: int = 10, show_border: bool = True) -> None:
#         """Layout-Generator Class. Used to create a layout on an Image object.
#
#         Args:
#             num_rows:
#                 number of rows for this layout.
#             num_cols:
#                 number of columns for this layout.
#             width:
#                 the absolute width of the canvas.
#             height:
#                 the absolute height of the canvas.
#             font_path:
#                 path to the font-file to use.
#             font_size:
#                 font size in pixels.
#             padding:
#                 see CSS padding.
#         """
#         self.num_rows = num_rows
#         self.num_cols = num_cols
#         self.row_height = int(height / self.num_rows) - 2 * padding
#         self.col_width = int(width / self.num_cols) - 2 * padding
#         self.font_path = font_path
#         self.font = ImageFont.truetype(font_path, size=16)
#         self.padding = padding
#         self.font_size = font_size
#         self.x = padding
#         self.y = padding
#         self.width = width - (2 * padding)
#         self.height = height - (2 * padding)
#         self.show_border = show_border
#         self.border_radius = border_radius
#         self.image = self.generate_layout()
#         self.draw = ImageDraw.Draw(self.image)
#
#     def generate_layout(self) -> Image:
#         """
#         Generate a blank layout image with the specified dimensions and padding
#         """
#         image = Image.new('L', (self.width, self.height), "white")
#         draw = ImageDraw.Draw(image)
#
#         for i in range(self.num_rows):
#             for j in range(self.num_cols):
#                 x0 = self.x + j * (self.col_width + self.padding)
#                 y0 = self.y + i * (self.row_height + self.padding)
#                 x1 = x0 + self.col_width
#                 y1 = y0 + self.row_height
#                 if self.show_border:
#                     draw.rounded_rectangle((x0, y0, x1, y1), outline="black", radius=self.border_radius)
#
#         self.image = image
#         return image
#
#     def get_cell_coordinates(self, row_number: int, col_number: int):
#         """Returns the specified cell's coordinates"""
#         x0 = (col_number - 1) * (self.col_width + self.padding)
#         y0 = (row_number - 1) * (self.row_height + self.padding)
#         x1 = x0 + self.col_width
#         y1 = y0 + self.row_height
#
#         return [x0, y0, x1, y1]
#
#     def set_font_size(self, font_size: int):
#         self.font = ImageFont.truetype(self.font_path, size=font_size)
#
#     def add_wrapped_text(self, text, row, col, alignment=TextAlignment.CENTER,
#                          color=InkycalColours.BLACK):
#         """
#         Add wrapped text to the specified cell in the layout
#         """
#         self.line_spacing = 0
#         if row < 1 or row > self.num_rows or col < 1 or col > self.num_cols:
#             raise ValueError(f"Invalid row or column: row={row}, col={col}")
#
#         x0 = self.x + (col - 1) * (self.col_width + self.padding)
#         y0 = self.y + (row - 1) * (self.row_height + self.padding)
#         x1 = x0 + self.col_width
#         y1 = y0 + self.row_height
#
#         self.set_font_size(self.font_size)
#
#         text_bbox = self.font.getbbox(text)
#         text_width = text_bbox[2] - text_bbox[0]
#         text_height = text_bbox[3] - text_bbox[1]
#
#         lines = []
#         words = text.split()
#         current_line = words[0]
#         for word in words[1:]:
#             line_bbox = self.draw.textbbox((0, 0), current_line + ' ' + word, font=self.font)
#             line_width = line_bbox[2] - line_bbox[0]
#             if line_width <= self.col_width:
#                 current_line += ' ' + word
#             else:
#                 lines.append(current_line)
#                 current_line = word
#         lines.append(current_line)
#
#         num_lines = len(lines)
#         total_height = num_lines * text_height + (num_lines - 1) * self.line_spacing
#         if total_height > self.row_height:
#             raise ValueError(f"Text too long to fit in cell: row={row}, col={col}")
#
#         y_start = y0 + (self.row_height - total_height) / 2
#         for line in lines:
#             line_bbox = self.draw.textbbox((0, 0), line, font=self.font)
#             line_width = line_bbox[2] - line_bbox[0]
#             if alignment == TextAlignment.LEFT:
#                 x_start = x0
#             elif alignment == TextAlignment.RIGHT:
#                 x_start = x1 - line_width
#             else:  # TextAlignment.CENTER
#                 x_start = x0 + (self.col_width - line_width) / 2
#             self.draw.text((x_start, y_start), line, fill=color.value, stroke_fill=color.value, font=self.font)
#             y_start += text_height + self.line_spacing
#
#     def add_text(self, text: str, row: int, col: int, alignment: TextAlignment = TextAlignment.CENTER,
#                  color: InkycalColours = InkycalColours.BLACK):
#         """
#         Add text to the specified cell in the layout
#         """
#         if row < 1 or row > self.num_rows or col < 1 or col > self.num_cols:
#             raise ValueError(f"Invalid row or column: row={row}, col={col}")
#
#         x0 = self.x + (col - 1) * (self.col_width + self.padding)
#         y0 = self.y + (row - 1) * (self.row_height + self.padding)
#
#         # Update the font size
#         self.set_font_size(self.font_size)
#
#         text_bbox = self.font.getbbox(text)
#         text_width = text_bbox[2] - text_bbox[0]
#         text_height = text_bbox[3] - text_bbox[1]
#
#         if text_width > self.col_width:
#             raise ValueError(f"Text is too wide for column: {text_width} > {self.col_width}")
#         if text_height > self.row_height:
#             raise ValueError(f"Text is too high for row: {text_height} > {self.row_height}")
#
#         # Add text to cell
#         if alignment == TextAlignment.LEFT:
#             x0 = self.x + (col - 1) * (self.col_width + self.padding)
#         elif alignment == TextAlignment.RIGHT:
#             x0 = self.x + (col - 1) * (self.col_width + self.padding) + self.col_width - text_width
#         elif alignment == TextAlignment.TOP:
#             y0 = self.y + (row - 1) * (self.row_height + self.padding)
#         elif alignment == TextAlignment.BOTTOM:
#             y0 = self.y + (row - 1) * (self.row_height + self.padding) + self.row_height - text_height
#         else:  # TextAlignment.CENTER
#             x0 = self.x + (col - 1) * (self.col_width + self.padding) + (self.col_width - text_width) / 2
#             y0 = self.y + (row - 1) * (self.row_height + self.padding) + (self.row_height - text_height) / 2
#         self.draw.text((x0, y0), text, fill=color.value, stroke_fill=color.value)
#
#
# # Works well (7/10)
# def convert_to_1bit(image, threshold: int = None):
#     """
#     Converts a grayscale image with only text to 1-bit mode suitable for reading on 1-bit e-paper displays
#
#     Args:
#     image: A grayscale PIL Image object
#
#     Returns:
#     A 1-bit PIL Image object
#     """
#
#     # Convert the image to mode "L" if it is not already in grayscale
#     if image.mode != "L":
#         image = image.convert("L")
#
#     # Calculate the optimal threshold for the image
#     if not threshold:
#         threshold = image.getextrema()[0] + (image.getextrema()[1] - image.getextrema()[0]) / 2
#
#     # Convert the image to 1-bit mode using the calculated threshold
#     return image.point(lambda x: 255 if x > threshold else 0, "1")
#
#
# def optimize_im(image, threshold=220):
#     """Optimize the image for rendering on ePaper displays"""
#
#     buffer = numpy.array(image.convert('RGB'))
#     red, green = buffer[:, :, 0], buffer[:, :, 1]
#
#     # grey->black
#     buffer[numpy.logical_and(red <= threshold, green <= threshold)] = [0, 0, 0]
#     image = Image.fromarray(buffer)
#     return image
#

class Widget:
    def __init__(self, width: int, height: int, font_path: str, font_size: int = 1, padding: int = 10,
                 style: str = "filled") -> None:
        """Widget-Generator Class. Used to create a layout on an Image object.

        Args:
            width:
                the absolute width of the canvas.
            height:
                the absolute height of the canvas.
            font_path:
                path to the font-file to use.
            font_size:
                font size in pixels.
            padding:
                margin around the actual widget.
            style:
                choose from "fill" or "border"
        """
        assert style in ("fill", "border")

        self.font_path = font_path
        self.font = InkycalFont(self.font_path, font_size_px=font_size)
        self.padding = padding
        self.font_size = font_size
        self.x = padding
        self.y = padding
        self.outer_width = width
        self.outer_height = height
        self.width = width - (2 * padding)
        self.height = height - (2 * padding)
        self.style = style

        self.font_image = None
        self.char_boxes = None
        self.set_font(self.font_path)
        self.cursor_x, self.cursor_y = padding, padding
        self.draw = None
        self.image = None
        self.create_widget()


    def create_widget(self) -> None:
        """
        Generate a blank layout image with the specified dimensions and padding
        """
        image = Image.new('RGBA', size=(self.width, self.height), color='white')

        # Create a widget
        widget_width = int(self.width - (2 * self.padding))
        widget_height = int(self.height - (2 * self.padding))
        logger.info(f'inner size: {widget_width}x{widget_height}px')

        draw = ImageDraw.Draw(image)

        self.draw = draw
        self.image = image

    def set_font(self, font_path):
        """Set a font by providing its path."""
        assert os.path.exists(font_path)
        self.font_path = font_path
        self.font = InkycalFont(self.font_path, font_size_px=self.font_size)
        image_path = f"{self.font.converted_font_directory}/{self.font_size}.png"
        char_json_path = f"{self.font.converted_font_directory}/{self.font_size}.json"

        if not os.path.exists(image_path) or not os.path.exists(char_json_path):
            raise AssertionError("Font does not exist or converted files are missing.")

        # Load the image with all characters
        self.font_image = Image.open(image_path)

        # Load the character box coordinates from the JSON file
        with open(char_json_path, 'r') as json_file:
            self.char_boxes = json.load(json_file)

    def get_font_height(self):
        """Get the height of the used font in pixels"""
        return self.font_image.height

    def get_width_of_text(self, text:str):
        """Get the width of the text when using the current font"""
        width = 0
        for char in text:
            if str(ord(char)) in self.char_boxes:
                box_coordinates = self.char_boxes[str(ord(char))]
                width += box_coordinates[2] - box_coordinates[0] + 1  # Move to the next character position
        return width

    def set_font_size(self, font_size: int):
        """Set the font-size."""
        self.font_size = font_size
        self.set_font(self.font_path)

    def write(self, text: str, coords: [int, int, int, int], align_x: str = "left", align_y: str = "center", use_maximum_font_size:bool=False) -> None:
        """Write a text on the widget. The cursor will automatically shift according

        Args:
            text:
                The text to draw
            coords:
                the bounding box coordinates (x0, y0, x1, y1)
            align_x:
                Text alignment in x-axis. Choose from "left", "center", "right". Default is "left"
            align_y:
                Text alignment in y-axis. Choose from "top", "center", "bottom". Default is "center"
            use_maximum_font_size:
                Use the maximum possible font-size to fill the given space

        Returns:
            None
        """

        assert align_x in ("left", "center", "right")
        assert align_y in ("top", "center", "bottom")

        # subtract 1 from the width and height so that the text below does not overlap
        coords = list(coords)
        coords[2] -= 1
        coords[3] -= 1

        textbox_max_height = coords[-1] - coords[1]
        textbox_max_width = coords[2] - coords[0]

        initial_font_size = self.font_size
        if use_maximum_font_size:
            font_size = self.font_size
            while textbox_max_width > self.get_width_of_text(text+ len(text)*" ") and textbox_max_height > self.get_font_height():
                font_size += 1
                self.set_font_size(font_size)
            self.set_font_size(font_size-1)


        width = 0
        for char in text:
            if str(ord(char)) in self.char_boxes.keys():
                box_coordinates = self.char_boxes[str(ord(char))]
                width += box_coordinates[2] - box_coordinates[0] + 1  # Move to the next character position

        assert 0 < width <= self.image.width

        # Create a new image with the same height as the font size and calculated width
        text_im = Image.new("L", (width, self.font_image.height), color=255)

        x = 0  # Initial x-coordinate
        for index, char in enumerate(text, start=1):
            if str(ord(char)) in self.char_boxes:
                box_coordinates = self.char_boxes[str(ord(char))]
                char_image = self.font_image.crop(box_coordinates)  # Crop the character from the source image
                text_im.paste(char_image, (x, 0))  # Paste the character onto the output image
                x += box_coordinates[2] - box_coordinates[0]  # Move to the next character position
                if index < len(text):
                    x+= 1
            else:
                logger.warning(f"Could not find character in font: {char} ({ord(char)})")

        assert (self.image.width >= text_im.width)
        assert (self.image.height >= text_im.height)
        assert (text_im.width <= textbox_max_width)
        assert (text_im.height <= textbox_max_height)

        x, y = 0, 0
        if align_x == "left":
            x = coords[0]
        elif align_x == "center":
            x = coords[0] + int((textbox_max_width - text_im.width) / 2)
        else:
            x = textbox_max_width - text_im.width

        if align_y == "top":
            y = coords[1]
        elif align_y == "center":
            y = coords[1] + int((textbox_max_height - text_im.height) / 2)
        else:
            y =textbox_max_height - text_im.height

        self.image.paste(text_im, (x,y))

        # self.draw.rectangle(coords, outline="gray") # for testing purposes

        self.set_font_size(initial_font_size)


    def get_image(self):
        """Get the image."""
        canvas = Image.new("RGB", (self.outer_width, self.outer_height), color="black")
        draw = ImageDraw.Draw(canvas)

        if self.style == "filled":
            im = ImageOps.invert(self.image)
            draw.rounded_rectangle(
                (1, 1, canvas.width-1, canvas.height-1), outline="black", fill="black", width=1, radius=self.image.width // 10)
        else:
            im = self.image
            draw.rounded_rectangle(
                (1, 1, canvas.width-1, canvas.height-1), outline="black", fill="white", width=1, radius=self.image.width // 10)

        canvas.paste(im, (self.padding, self.padding))
        return canvas
