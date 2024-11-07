"""
Inkycal command-line interface.

Please do not use. This is still in development and may not work as expected.

Usage:
1) python tui.py
2) select the correct display
3) press enter
4) wait for the image to appear on the display

"""

from textual import on
from textual.screen import Screen
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, OptionList, LoadingIndicator, Static
from textual.binding import Binding
from PIL import Image, ImageDraw, ImageFont
from inkycal.display import Display

displays = Display.get_display_names()
DEFAULT_FONT = "fonts/NotoSansUI/NotoSansUI-Bold.ttf"

class Help(Screen):
    """The help screen for the application."""

    BINDINGS = [("escape,space,q,question_mark", "pop_screen", "Close")]
    """Bindings for the help screen."""

    def compose(self) -> ComposeResult:
        """Compose the game's help.

        Returns:
            ComposeResult: The result of composing the help screen.
        """
        yield Static(" Windows ", id="title")
        yield Static("""This is a command-line interface written for Inkycal. It is used to test the display of your Inkycal device.""", id="description")
        yield Static("Please select a display to test. Then press enter. Only if the connections were correct and the display was correctly selected, you should see an image soon. Otherwise, you will get an error.", id="instructions")
        yield Static("Press any key to continue [blink]_[/]", id="any-key")


class Loader(Static):
    """A stopwatch widget."""

    def compose(self) -> ComposeResult:
        """Create child widgets of a stopwatch."""
        yield LoadingIndicator()


class Calibrate(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding("d", "toggle_dark", "Toggle dark mode"),
        Binding(key="h", action="help", description="Show help screen", key_display="h"),
        Binding(key="enter", action="process", description="Select", show=False),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield OptionList(*displays)

    def on_mount(self) -> None:
        self.install_screen(Loader(), name="loader")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    @on(OptionList.OptionSelected)
    def action_process(self, event: OptionList.OptionSelected):
        """Handle selection from OptionList."""
        option_id = event.option_index
        display_name = displays[option_id]
        self.generate_image(display_name)
        self.show_image(display_name)
        self.bell()
        self.push_screen(Loader())

    def generate_image(self, display_name):
        """Generate an image with the specified text."""
        width, height = 400, 300  # Set the size of the image
        image = Image.new('1', (width, height), color=1)  # Create a white image
        draw = ImageDraw.Draw(image)

        # Load a font
        font = ImageFont.truetype(DEFAULT_FONT, 30)

        # Define the text
        text = f"Inkycal - by AceInnoLab\nDisplay test for:\n{display_name}"

        # Calculate text size and position
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2

        # Draw the text on the image
        draw.text((text_x, text_y), text, font=font, fill=0)  # Black text

        # Save the image
        image.save(f"display_test_{display_name}.png")
        print(f"Image saved as display_test_{display_name}.png")

    def show_image(self, display_name):
        """Show the generated image on the selected display."""
        display = Display(display_name)
        temp_path = f"display_test_{display_name}.png"
        im = Image.open(temp_path)
        optional_colour_image = Image.new("RGB", im.size, "white")
        display.render(im, optional_colour_image)

    def action_help(self) -> None:
        """Show the help screen."""
        self.push_screen(Help())


if __name__ == "__main__":
    app = Calibrate()
    app.run()