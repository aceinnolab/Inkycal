from enum import Enum

import math
import numpy
from PIL import Image, ImageDraw, ImageFont

from inkycal.display.inkycal_colours import InkycalColours


class TextAlignment(Enum):
    CENTER = 1
    LEFT = 2
    RIGHT = 3
    TOP = 4
    BOTTOM = 5


class LayoutGenerator:

    def __init__(self, num_rows: int, num_cols: int, width: int, height: int, font_path: str,
                 rem_size: int = 1, padding: int = 10, border_radius:int=10, show_border:bool=True) -> None:
        """Layout-Generator Class. Used to create a layout on an Image object.

        Args:
            num_rows:
                number of rows for this layout.
            num_cols:
                number of columns for this layout.
            width:
                the absolute width of the canvas.
            height:
                the absolute height of the canvas.
            font_path:
                path to the fontfile to use.
            rem_size:
                see CSS rem size. Multiple of 16px.
            padding:
                see CSS padding.
        """
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.row_height = int(height / self.num_rows) - 2 * padding
        self.col_width = int(width / self.num_cols) - 2 * padding
        self.font_path = font_path
        self.font = ImageFont.truetype(font_path, size=16)
        self.padding = padding
        self.rem_size = rem_size
        self.x = padding
        self.y = padding
        self.width = width - (2 * padding)
        self.height = height - (2 * padding)
        self.show_border = show_border
        self.border_radius = border_radius
        self.image = self.generate_layout()
        self.draw = ImageDraw.Draw(self.image)

    def generate_layout(self) -> Image:
        """
        Generate a blank layout image with the specified dimensions and padding
        """
        image = Image.new('L', (self.width, self.height), "white")
        draw = ImageDraw.Draw(image)

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                x0 = self.x + j * (self.col_width + self.padding)
                y0 = self.y + i * (self.row_height + self.padding)
                x1 = x0 + self.col_width
                y1 = y0 + self.row_height
                if self.show_border:
                    draw.rounded_rectangle((x0, y0, x1, y1), outline="black", radius=self.border_radius)

        self.image = image
        return image

    def set_font_size(self, font_size: int):
        self.font = ImageFont.truetype(self.font_path, size=font_size)

    def add_text(self, text: str, row: int, col: int, alignment: TextAlignment = TextAlignment.CENTER,
                 wrap_text: bool = False, color:InkycalColours=InkycalColours.BLACK):
        """
        Add text to the specified cell in the layout
        """
        self.line_spacing = 0
        if row < 1 or row > self.num_rows or col < 1 or col > self.num_cols:
            raise ValueError(f"Invalid row or column: row={row}, col={col}")

        x0 = self.x + (col - 1) * (self.col_width + self.padding)
        y0 = self.y + (row - 1) * (self.row_height + self.padding)
        x1 = x0 + self.col_width
        y1 = y0 + self.row_height

        # Update the font size
        self.set_font_size(self.rem_size * 13)

        if wrap_text:
            text_bbox = self.font.getbbox(text)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            if text_width <= self.col_width:
                # Text fits in one line
                if alignment == TextAlignment.LEFT:
                    x0 = x0
                    y0 = y0 + (self.row_height - text_height) / 2
                elif alignment == TextAlignment.RIGHT:
                    x0 = x1 - text_width
                    y0 = y0 + (self.row_height - text_height) / 2
                elif alignment == TextAlignment.TOP:
                    x0 = x0 + (self.col_width - text_width) / 2
                    y0 = y0
                elif alignment == TextAlignment.BOTTOM:
                    x0 = x0 + (self.col_width - text_width) / 2
                    y0 = y1 - text_height
                else:  # TextAlignment.CENTER
                    x0 = x0 + (self.col_width - text_width) / 2
                    y0 = y0 + (self.row_height - text_height) / 2

                self.draw.text((x0, y0), text, fill=color.value, stroke_fill=color.value, font=self.font)
            else:
                # Text needs to be wrapped to multiple lines
                lines = []
                words = text.split()
                current_line = words[0]
                for word in words[1:]:
                    if self.draw.textsize(current_line + ' ' + word, font=self.font)[0] <= self.col_width:
                        current_line += ' ' + word
                    else:
                        lines.append(current_line)
                        current_line = word
                lines.append(current_line)

                num_lines = len(lines)
                total_height = num_lines * text_height + (num_lines - 1) * self.line_spacing
                if total_height > self.row_height:
                    raise ValueError(f"Text too long to fit in cell: row={row}, col={col}")

                y_start = y0 + (self.row_height - total_height) / 2
                for line in lines:
                    line_width, _ = self.draw.textsize(line, font=self.font)
                    if alignment == TextAlignment.LEFT:
                        x_start = x0
                    elif alignment == TextAlignment.RIGHT:
                        x_start = x1 - line_width
                    else:  # TextAlignment.CENTER
                        x_start = x0 + (self.col_width - line_width) / 2
                    self.draw.text((x_start, y_start), line, fill=color.value, stroke_fill=color.value, font=self.font)
                    y_start += text_height + self.line_spacing
        else:
            text_width, text_height = self.draw.textsize(text, font=self.font)
            # Check if text fits in the cell
            if not wrap_text and (text_width > self.col_width or text_height > self.row_height):
                raise ValueError("Text does not fit in cell")

            # Wrap text if necessary
            if wrap_text and text_width > self.col_width:
                # Calculate number of lines needed
                lines = int(math.ceil(text_width / self.col_width))

                # Split text into lines
                words = text.split(" ")
                lines_text = []
                curr_line = ""
                for word in words:
                    if self.draw.textsize(curr_line + " " + word, font=self.font)[0] > self.col_width:
                        lines_text.append(curr_line.strip())
                        curr_line = word + " "
                    else:
                        curr_line += word + " "
                lines_text.append(curr_line.strip())

                # Check if wrapped text fits in cell
                if len(lines_text) > self.num_rows - row + 1:
                    raise ValueError("Wrapped text does not fit in cell")

                # Add each line of text to the cell
                for i, line in enumerate(lines_text):
                    line_width, line_height = self.draw.textsize(line, font=self.font)
                    if alignment == TextAlignment.LEFT:
                        x0 = self.x + (col - 1) * (self.col_width + self.padding)
                    elif alignment == TextAlignment.RIGHT:
                        x0 = self.x + (col - 1) * (self.col_width + self.padding) + self.col_width - line_width
                    elif alignment == TextAlignment.TOP:
                        y0 = self.y + (row - 1 + i) * (self.row_height + self.padding)
                    elif alignment == TextAlignment.BOTTOM:
                        y0 = self.y + (row - 1 + i) * (self.row_height + self.padding) + self.row_height - line_height
                    else:  # TextAlignment.CENTER
                        x0 = self.x + (col - 1) * (self.col_width + self.padding) + (self.col_width - line_width) / 2
                        y0 = self.y + (row - 1 + i) * (self.row_height + self.padding) + (
                                self.row_height - line_height) / 2
                    self.draw.text((x0, y0), line, font=self.font, fill=color.value, stroke_fill=color.value)
            else:
                # Add text to cell
                if alignment == TextAlignment.LEFT:
                    x0 = self.x + (col - 1) * (self.col_width + self.padding)
                elif alignment == TextAlignment.RIGHT:
                    x0 = self.x + (col - 1) * (self.col_width + self.padding) + self.col_width - text_width
                elif alignment == TextAlignment.TOP:
                    y0 = self.y + (row - 1) * (self.row_height + self.padding)
                elif alignment == TextAlignment.BOTTOM:
                    y0 = self.y + (row - 1) * (self.row_height + self.padding) + self.row_height - text_height
                else:  # TextAlignment.CENTER
                    x0 = self.x + (col - 1) * (self.col_width + self.padding) + (self.col_width - text_width) / 2
                    y0 = self.y + (row - 1) * (self.row_height + self.padding) + (self.row_height - text_height) / 2
                self.draw.text((x0, y0), text)
                if not wrap_text:
                    if text_width > self.col_width:
                        raise ValueError(f"Text is too wide for column: {text_width} > {self.col_width}")
                    if text_height > self.row_height:
                        raise ValueError(f"Text is too high for row: {text_height} > {self.row_height}")
                    self.draw.text((x0, y0), text, fill=color.value, stroke_fill=color.value)
                else:
                    # wrap the text to fit within the cell
                    words = text.split()
                    wrapped_lines = []
                    current_line = words[0]
                    for word in words[1:]:
                        width, _ = self.draw.textsize(current_line + ' ' + word, font=self.font)
                        if width < self.col_width:
                            current_line += ' ' + word
                        else:
                            wrapped_lines.append(current_line)
                            current_line = word
                    wrapped_lines.append(current_line)

                    # check if wrapped text can fit in the column/row
                    num_lines = len(wrapped_lines)
                    if num_lines > 1 and num_lines * text_height > self.row_height:
                        raise ValueError(
                            f"Wrapped text is too high for row: {num_lines * text_height} > {self.row_height}")
                    elif max([self.draw.textsize(line, font=self.font)[0] for line in wrapped_lines]) > self.col_width:
                        raise ValueError(
                            f"Wrapped text is too wide for column: {max([self.draw.textsize(line, font=self.font)[0] for line in wrapped_lines])} > {self.col_width}")

                    # write the wrapped text to the image
                    for i, line in enumerate(wrapped_lines):
                        line_width, _ = self.draw.textsize(line, font=self.font)
                        line_x0 = x0 + (self.col_width - line_width) / 2
                        line_y0 = y0 + (i * text_height)
                        self.draw.text((line_x0, line_y0), line, fill=color.value, stroke_fill=color.value)


# Works well (7/10)
def convert_to_1bit(image, threshold: int = None):
    """
    Converts a grayscale image with only text to 1-bit mode suitable for reading on 1-bit e-paper displays

    Args:
    image: A grayscale PIL Image object

    Returns:
    A 1-bit PIL Image object
    """

    # Convert the image to mode "L" if it is not already in grayscale
    if image.mode != "L":
        image = image.convert("L")

    # Calculate the optimal threshold for the image
    if not threshold:
        threshold = image.getextrema()[0] + (image.getextrema()[1] - image.getextrema()[0]) / 2

    # Convert the image to 1-bit mode using the calculated threshold
    return image.point(lambda x: 255 if x > threshold else 0, "1")


def optimize_im(image, threshold=220):
    """Optimize the image for rendering on ePaper displays"""

    buffer = numpy.array(image.convert('RGB'))
    red, green = buffer[:, :, 0], buffer[:, :, 1]

    # grey->black
    buffer[numpy.logical_and(red <= threshold, green <= threshold)] = [0, 0, 0]
    image = Image.fromarray(buffer)
    return image


if __name__ == '__main__':
    im = Image.new(mode="L", size=(600, 400), color="white")
    canvas = LayoutGenerator(num_rows=2, num_cols=3, width=600, height=400,
                             font_path="/Users/ace/Desktop/Projekte/Inkycal/logs/Roboto/Roboto-Medium.ttf", padding=5)
    # font_path = "/Users/ace/Desktop/Projekte/Inkycal/logs/VCR/VCR_OSD_MONO_1.001.ttf", padding = 5)
    canvas.add_text(
        text="Row 1 Col1 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.".upper(),
        row=1, col=1, wrap_text=True, alignment=TextAlignment.LEFT)
    canvas.add_text(
        text="Row 1 Col2 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit.",
        row=1, col=2, wrap_text=True)
    canvas.add_text(
        text="Row 1 Col3 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit.",
        row=1, col=3, wrap_text=True, alignment=TextAlignment.RIGHT)
    canvas.add_text(
        text="Row 2 Col1 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit.",
        row=2, col=1, wrap_text=True, alignment=TextAlignment.RIGHT)
    canvas.add_text(
        text="Row 2 Col2 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit.",
        row=2, col=2, wrap_text=True)
    canvas.add_text(
        text="Row 2 Col3 Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit.",
        row=2, col=3, wrap_text=True, alignment=TextAlignment.LEFT)
    # canvas.image.show()
    canvas.image.convert("1", dither=False)
    canvas_mod = convert_to_1bit(canvas.image, threshold=220)
    canvas_mod.show()
    print("Complete")
