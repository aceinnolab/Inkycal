#!/usr/bin/env python3
"""
Universal E-Paper Display Test Script for Inkycal
Tests displays with various patterns for validation
Supports both color (3-color) and black/white displays
"""

import sys
import time
import json
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

sys.path.insert(0, str(Path(__file__).parent))

from inkycal.display.display import Display
from inkycal.display.supported_models import supported_models
from inkycal.settings import Settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalDisplayTest:
    def __init__(self, model=None, auto_detect=True):
        """Initialize the display test class
        
        Args:
            model: Display model name (optional)
            auto_detect: Try to detect from settings.json if model not provided
        """
        self.model = model
        self.display = None
        self.width = None
        self.height = None
        self.is_colour = False
        
        # Color definitions
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        
        # Auto-detect model if needed
        if not self.model and auto_detect:
            self.model = self._auto_detect_model()
        
        if not self.model:
            raise ValueError("No display model specified. Use --model or ensure settings.json exists")
        
        # Validate and get display info
        self._validate_model()
        
        # Initialize display
        self._init_display()
        
    def _auto_detect_model(self):
        """Try to detect display model from settings.json"""
        for settings_path in Settings.SETTINGS_JSON_PATHS:
            settings_file = Path(settings_path)
            if settings_file.exists():
                try:
                    with open(settings_file, 'r') as f:
                        settings = json.load(f)
                        model = settings.get('model')
                        if model:
                            logger.info(f"Auto-detected model '{model}' from {settings_path}")
                            return model
                except Exception as e:
                    logger.warning(f"Could not read {settings_path}: {e}")
        
        logger.warning("Could not auto-detect display model from settings.json")
        return None
    
    def _validate_model(self):
        """Validate the display model and get its properties"""
        if self.model not in supported_models:
            logger.error(f"Model '{self.model}' not supported")
            logger.info("Supported models:")
            for model_name in sorted(supported_models.keys()):
                width, height = supported_models[model_name]
                color_info = " (colour)" if "colour" in model_name.lower() else ""
                logger.info(f"  - {model_name}: {width}x{height}{color_info}")
            raise ValueError(f"Unsupported model: {self.model}")
        
        # Get display dimensions
        self.width, self.height = supported_models[self.model]
        
        # Check if it's a color display
        self.is_colour = "colour" in self.model.lower() or "color" in self.model.lower()
        
        logger.info(f"Display model: {self.model}")
        logger.info(f"Resolution: {self.width}x{self.height}")
        logger.info(f"Type: {'Colour (3-color)' if self.is_colour else 'Black/White'}")
    
    def _init_display(self):
        """Initialize the display hardware"""
        try:
            logger.info(f"Initializing {self.model} display...")
            self.display = Display(self.model)
            logger.info(f"Display initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize display: {e}")
            raise
    
    def clear_display(self):
        """Clear the display to white"""
        logger.info("Clearing display...")
        black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
        
        if self.is_colour:
            red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            self.display.render(black_img, red_img)
        else:
            self.display.render(black_img)
        
        logger.info("Display cleared")
    
    def test_solid_colors(self):
        """Test solid color fills"""
        logger.info("Testing solid colors...")
        
        # Test 1: Full black screen
        logger.info("Test 1: Full black screen")
        black_img = Image.new('RGB', (self.width, self.height), self.BLACK)
        if self.is_colour:
            red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            self.display.render(black_img, red_img)
        else:
            self.display.render(black_img)
        time.sleep(5)
        
        # Test 2: Full white screen
        logger.info("Test 2: Full white screen")
        black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
        if self.is_colour:
            red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            self.display.render(black_img, red_img)
        else:
            self.display.render(black_img)
        time.sleep(5)
        
        # Test 3: Full red screen (color displays only)
        if self.is_colour:
            logger.info("Test 3: Full red/color screen")
            black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            red_img = Image.new('RGB', (self.width, self.height), self.RED)
            self.display.render(black_img, red_img)
            time.sleep(5)
    
    def test_color_sections(self):
        """Test display with color sections"""
        if self.is_colour:
            logger.info("Testing color sections (thirds)...")
        else:
            logger.info("Testing black/white sections (halves)...")
        
        # Create images
        black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
        draw_black = ImageDraw.Draw(black_img)
        
        if self.is_colour:
            red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            draw_red = ImageDraw.Draw(red_img)
            
            # Divide screen into three vertical sections
            section_width = self.width // 3
            
            # Left section: Black
            draw_black.rectangle([0, 0, section_width, self.height], fill=self.BLACK)
            
            # Middle section: White (already white)
            
            # Right section: Red
            draw_red.rectangle([section_width * 2, 0, self.width, self.height], fill=self.RED)
            
            self.display.render(black_img, red_img)
        else:
            # For B/W displays: half black, half white
            section_width = self.width // 2
            draw_black.rectangle([0, 0, section_width, self.height], fill=self.BLACK)
            self.display.render(black_img)
        
        logger.info("Color sections displayed")
        time.sleep(5)
    
    def test_checkerboard(self):
        logger.info("Testing checkerboard pattern...")
        
        black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
        draw_black = ImageDraw.Draw(black_img)
        
        if self.is_colour:
            red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            draw_red = ImageDraw.Draw(red_img)
        
        # Adjust square size based on display size
        square_size = max(20, min(50, self.width // 20))
        
        for y in range(0, self.height, square_size):
            for x in range(0, self.width, square_size):
                if self.is_colour:
                    # For color displays: cycle through black, white, red
                    pattern = ((x // square_size) + (y // square_size)) % 3
                    if pattern == 0:
                        draw_black.rectangle([x, y, x + square_size, y + square_size], fill=self.BLACK)
                    elif pattern == 1:
                        draw_red.rectangle([x, y, x + square_size, y + square_size], fill=self.RED)
                else:
                    # For B/W displays: simple checkerboard
                    if ((x // square_size) + (y // square_size)) % 2 == 0:
                        draw_black.rectangle([x, y, x + square_size, y + square_size], fill=self.BLACK)
        
        if self.is_colour:
            self.display.render(black_img, red_img)
        else:
            self.display.render(black_img)
        
        logger.info("Checkerboard pattern displayed")
        time.sleep(5)
    
    def test_geometric_shapes(self):
        logger.info("Testing geometric shapes...")
        
        black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
        draw_black = ImageDraw.Draw(black_img)
        
        if self.is_colour:
            red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            draw_red = ImageDraw.Draw(red_img)
        
        # Scale shapes based on display size
        scale = min(self.width, self.height) / 400
        
        # Black circle
        circle_size = int(100 * scale)
        draw_black.ellipse([50, 50, 50 + circle_size, 50 + circle_size], fill=self.BLACK)
        
        # Rectangle (red for color, black for B/W)
        rect_x = int(200 * scale)
        rect_size = int(100 * scale)
        if self.is_colour:
            draw_red.rectangle([rect_x, 50, rect_x + rect_size, 50 + rect_size], fill=self.RED)
        else:
            draw_black.rectangle([rect_x, 50, rect_x + rect_size, 50 + rect_size], fill=self.BLACK)
        
        # Cross lines
        draw_black.line([0, self.height//2, self.width, self.height//2], fill=self.BLACK, width=3)
        draw_black.line([self.width//2, 0, self.width//2, self.height], fill=self.BLACK, width=3)
        
        # Diagonal lines (red for color displays)
        if self.is_colour:
            draw_red.line([0, 0, self.width, self.height], fill=self.RED, width=2)
            draw_red.line([self.width, 0, 0, self.height], fill=self.RED, width=2)
        else:
            draw_black.line([0, 0, self.width, self.height], fill=self.BLACK, width=1)
            draw_black.line([self.width, 0, 0, self.height], fill=self.BLACK, width=1)
        
        if self.is_colour:
            self.display.render(black_img, red_img)
        else:
            self.display.render(black_img)
        
        logger.info("Geometric shapes displayed")
        time.sleep(5)
    
    def test_text_rendering(self):
        logger.info("Testing text rendering...")
        
        black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
        draw_black = ImageDraw.Draw(black_img)
        
        if self.is_colour:
            red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            draw_red = ImageDraw.Draw(red_img)
        
        # Scale font sizes based on display size
        scale = min(self.width, self.height) / 400
        
        # Try to load fonts
        try:
            font_small = ImageFont.truetype(f"{Settings.FONT_PATH}/NotoSans-Light.ttf", int(16 * scale))
            font_medium = ImageFont.truetype(f"{Settings.FONT_PATH}/NotoSans-Regular.ttf", int(24 * scale))
            font_large = ImageFont.truetype(f"{Settings.FONT_PATH}/NotoSans-Bold.ttf", int(36 * scale))
        except:
            logger.warning("Custom fonts not found, using default")
            font_small = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_large = ImageFont.load_default()
        
        y_offset = 20
        
        # Title
        draw_black.text((20, y_offset), "E-Paper Display Test", font=font_large, fill=self.BLACK)
        y_offset += int(50 * scale)
        
        # Display info
        info_text = [
            f"Model: {self.model}",
            f"Resolution: {self.width} x {self.height}",
            f"Type: {'Colour' if self.is_colour else 'Black/White'}",
            f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        ]
        
        for i, text in enumerate(info_text):
            if self.is_colour and i % 2 == 1:
                draw_red.text((20, y_offset), text, font=font_medium, fill=self.RED)
            else:
                draw_black.text((20, y_offset), text, font=font_medium, fill=self.BLACK)
            y_offset += int(35 * scale)
        
        # Sample text
        y_offset += int(20 * scale)
        draw_black.text((20, y_offset), "The quick brown fox jumps over the lazy dog", 
                       font=font_small, fill=self.BLACK)
        
        if self.is_colour:
            y_offset += int(25 * scale)
            draw_red.text((20, y_offset), "0123456789 !@#$%^&*()", 
                         font=font_small, fill=self.RED)
        
        if self.is_colour:
            self.display.render(black_img, red_img)
        else:
            self.display.render(black_img)
        
        logger.info("Text rendering displayed")
        time.sleep(5)
    
    def test_gradient_bars(self):
        logger.info("Testing gradient/dither patterns...")
        
        black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
        draw_black = ImageDraw.Draw(black_img)
        
        if self.is_colour:
            red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            draw_red = ImageDraw.Draw(red_img)
        
        # Create horizontal bars with different patterns
        num_bars = 4 if self.is_colour else 3
        bar_height = self.height // num_bars
        
        # Bar 1: Dithered black gradient
        for x in range(self.width):
            if x % 2 == 0 or x < self.width // 3:
                draw_black.line([(x, 0), (x, bar_height)], fill=self.BLACK)
        
        # Bar 2: For color displays, dithered red
        if self.is_colour:
            for x in range(self.width):
                if x % 2 == 0 or x < self.width // 3:
                    draw_red.line([(x, bar_height), (x, bar_height * 2)], fill=self.RED)
            bar_start = 2
        else:
            bar_start = 1
        
        # Vertical stripes
        stripe_width = 10
        for x in range(0, self.width, stripe_width * 2):
            draw_black.rectangle([x, bar_height * bar_start, x + stripe_width, bar_height * (bar_start + 1)], 
                                fill=self.BLACK)
        
        # Fine checkerboard at bottom
        for x in range(0, self.width, 4):
            for y in range(bar_height * (num_bars - 1), self.height, 4):
                if ((x // 4) + (y // 4)) % 2 == 0:
                    draw_black.rectangle([x, y, x + 4, y + 4], fill=self.BLACK)
        
        if self.is_colour:
            self.display.render(black_img, red_img)
        else:
            self.display.render(black_img)
        
        logger.info("Gradient/dither patterns displayed")
        time.sleep(5)
    
    def test_calibration_pattern(self):
        """Display calibration pattern for alignment testing"""
        logger.info("Testing calibration pattern...")
        
        black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
        draw_black = ImageDraw.Draw(black_img)
        
        if self.is_colour:
            red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            draw_red = ImageDraw.Draw(red_img)
        
        # Draw border
        draw_black.rectangle([0, 0, self.width-1, self.height-1], outline=self.BLACK, width=3)
        
        # Inner border (red for color displays)
        if self.is_colour:
            draw_red.rectangle([10, 10, self.width-11, self.height-11], outline=self.RED, width=2)
        else:
            draw_black.rectangle([10, 10, self.width-11, self.height-11], outline=self.BLACK, width=1)
        
        # Center crosshair
        center_x = self.width // 2
        center_y = self.height // 2
        cross_size = min(50, self.width // 10)
        
        draw_black.line([center_x - cross_size, center_y, center_x + cross_size, center_y], 
                       fill=self.BLACK, width=2)
        draw_black.line([center_x, center_y - cross_size, center_x, center_y + cross_size], 
                       fill=self.BLACK, width=2)
        
        # Corner markers
        marker_size = min(50, self.width // 10)
        
        # Top-left
        draw_black.line([0, marker_size, marker_size, marker_size], fill=self.BLACK, width=2)
        draw_black.line([marker_size, 0, marker_size, marker_size], fill=self.BLACK, width=2)
        
        # Top-right
        draw_black.line([self.width - marker_size, 0, self.width - marker_size, marker_size], 
                       fill=self.BLACK, width=2)
        draw_black.line([self.width - marker_size, marker_size, self.width, marker_size], 
                       fill=self.BLACK, width=2)
        
        # Bottom corners (red for color displays)
        if self.is_colour:
            # Bottom-left
            draw_red.line([0, self.height - marker_size, marker_size, self.height - marker_size], 
                         fill=self.RED, width=2)
            draw_red.line([marker_size, self.height - marker_size, marker_size, self.height], 
                         fill=self.RED, width=2)
            
            # Bottom-right
            draw_red.line([self.width - marker_size, self.height - marker_size, 
                          self.width - marker_size, self.height], fill=self.RED, width=2)
            draw_red.line([self.width - marker_size, self.height - marker_size, 
                          self.width, self.height - marker_size], fill=self.RED, width=2)
        else:
            # Bottom-left
            draw_black.line([0, self.height - marker_size, marker_size, self.height - marker_size], 
                           fill=self.BLACK, width=2)
            draw_black.line([marker_size, self.height - marker_size, marker_size, self.height], 
                           fill=self.BLACK, width=2)
            
            # Bottom-right
            draw_black.line([self.width - marker_size, self.height - marker_size, 
                           self.width - marker_size, self.height], fill=self.BLACK, width=2)
            draw_black.line([self.width - marker_size, self.height - marker_size, 
                           self.width, self.height - marker_size], fill=self.BLACK, width=2)
        
        # Grid
        grid_spacing = max(50, min(100, self.width // 10))
        for x in range(0, self.width, grid_spacing):
            draw_black.line([x, 0, x, self.height], fill=self.BLACK, width=1)
        for y in range(0, self.height, grid_spacing):
            draw_black.line([0, y, self.width, y], fill=self.BLACK, width=1)
        
        if self.is_colour:
            self.display.render(black_img, red_img)
        else:
            self.display.render(black_img)
        
        logger.info("Calibration pattern displayed")
        time.sleep(5)
    
    def run_calibration_cycles(self, cycles=3):
        """Run calibration cycles to refresh the display"""
        logger.info(f"Running {cycles} calibration cycles...")
        
        for i in range(cycles):
            logger.info(f"Calibration cycle {i+1}/{cycles}")
            
            # Black
            black_img = Image.new('RGB', (self.width, self.height), self.BLACK)
            if self.is_colour:
                red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
                self.display.render(black_img, red_img)
            else:
                self.display.render(black_img)
            time.sleep(2)
            
            # White
            black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
            if self.is_colour:
                red_img = Image.new('RGB', (self.width, self.height), self.WHITE)
                self.display.render(black_img, red_img)
            else:
                self.display.render(black_img)
            time.sleep(2)
            
            # Red (color displays only)
            if self.is_colour:
                black_img = Image.new('RGB', (self.width, self.height), self.WHITE)
                red_img = Image.new('RGB', (self.width, self.height), self.RED)
                self.display.render(black_img, red_img)
                time.sleep(2)
        
        logger.info("Calibration cycles complete")
    
    def run_all_tests(self, delay_between_tests=3):
        """Run all test patterns in sequence"""
        logger.info(f"Starting comprehensive display test for {self.model}...")
        
        tests = [
            ("Clear Display", self.clear_display),
            ("Solid Colors", self.test_solid_colors),
            ("Color Sections", self.test_color_sections),
            ("Checkerboard Pattern", self.test_checkerboard),
            ("Geometric Shapes", self.test_geometric_shapes),
            ("Text Rendering", self.test_text_rendering),
            ("Gradient/Dither Patterns", self.test_gradient_bars),
            ("Calibration Pattern", self.test_calibration_pattern),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Running: {test_name} ---")
            try:
                test_func()
                time.sleep(delay_between_tests)
            except Exception as e:
                logger.error(f"Test '{test_name}' failed: {e}")
                continue
        
        logger.info("\nAll tests completed!")
    
    def cleanup(self):
        """Clean up display resources"""
        logger.info("Cleaning up...")
        if self.display:
            self.clear_display()
        logger.info("Cleanup complete")


def list_supported_displays():
    """List all supported display models"""
    print("\nSupported E-Paper Display Models:")
    print("-" * 50)
    
    # Separate color and B/W displays
    color_displays = []
    bw_displays = []
    
    for model_name in sorted(supported_models.keys()):
        if model_name == "image_file":
            continue  # Skip the virtual display
        
        width, height = supported_models[model_name]
        info = f"{model_name}: {width}x{height}"
        
        if "colour" in model_name.lower() or "color" in model_name.lower():
            color_displays.append(info)
        else:
            bw_displays.append(info)
    
    print("\nColor Displays (3-color: black/white/red):")
    for display in color_displays:
        print(f"  - {display}")
    
    print("\nBlack/White Displays:")
    for display in bw_displays:
        print(f"  - {display}")
    
    print("\nVirtual Display (for testing without hardware):")
    print(f"  - image_file: {supported_models['image_file'][0]}x{supported_models['image_file'][1]}")
    
    print("\nUsage: python test_display.py --model <model_name>")
    print("   or: python test_display.py (auto-detect from settings.json)")


def main():
    """Main function to run display tests"""
    parser = argparse.ArgumentParser(description='Universal E-Paper Display Test Script')
    parser.add_argument('--model', type=str, default=None,
                       help='Display model name (e.g., epd_7_in_5_colour, epd_12_in_48_colour_V2)')
    parser.add_argument('--test', type=str, default='all',
                       choices=['all', 'solid', 'sections', 'checkerboard', 'shapes', 
                               'text', 'gradient', 'calibration', 'cycles'],
                       help='Specific test to run (default: all)')
    parser.add_argument('--cycles', type=int, default=3,
                       help='Number of calibration cycles (default: 3)')
    parser.add_argument('--delay', type=int, default=3,
                       help='Delay between tests in seconds (default: 3)')
    parser.add_argument('--list', action='store_true',
                       help='List all supported display models')
    parser.add_argument('--no-auto', action='store_true',
                       help='Disable auto-detection from settings.json')
    
    args = parser.parse_args()
    
    # List supported displays if requested
    if args.list:
        list_supported_displays()
        return 0
    
    # Create test instance
    try:
        tester = UniversalDisplayTest(
            model=args.model,
            auto_detect=not args.no_auto
        )
    except Exception as e:
        logger.error(f"Failed to initialize display test: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Make sure you're running on a Raspberry Pi with display connected")
        logger.error("2. Check that SPI is enabled (sudo raspi-config)")
        logger.error("3. Try with sudo if you get permission errors")
        logger.error("4. Use --list to see all supported models")
        logger.error("5. Use --model to specify your display model explicitly")
        return 1
    
    try:
        # Run requested test
        if args.test == 'all':
            tester.run_all_tests(delay_between_tests=args.delay)
        elif args.test == 'solid':
            tester.test_solid_colors()
        elif args.test == 'sections':
            tester.test_color_sections()
        elif args.test == 'checkerboard':
            tester.test_checkerboard()
        elif args.test == 'shapes':
            tester.test_geometric_shapes()
        elif args.test == 'text':
            tester.test_text_rendering()
        elif args.test == 'gradient':
            tester.test_gradient_bars()
        elif args.test == 'calibration':
            tester.test_calibration_pattern()
        elif args.test == 'cycles':
            tester.run_calibration_cycles(cycles=args.cycles)
        
        # Always clear display at the end
        time.sleep(2)
        tester.cleanup()
        
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        tester.cleanup()
        return 0
    except Exception as e:
        logger.error(f"Test failed: {e}")
        tester.cleanup()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
