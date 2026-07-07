supported_models = {
    "epd_13_in_3": (960, 680),
    "epd_13_in_3_colour": (960, 680),
    "epd_12_in_48": (1304, 984),
    "epd_7_in_5_colour": (640, 384),
    "9_in_7": (1200, 825),
    "epd_5_in_83_colour": (600, 448),
    "epd_12_in_48_colour": (1304, 984),
    "epd_4_in_2_colour": (400, 300),
    "epd_7_in_5_v2": (800, 480),
    "epd_12_in_48_colour_V2": (1304, 984),
    "epd_7_in_5": (640, 384),
    "epd_5_in_83_V2": (648, 480),
    "epd5in83b_V2": (648, 480),
    "epd_7_in_5_v3": (880, 528),
    "10_in_3": (1872, 1404),
    "epd_7_in_5_v2_colour": (800, 480),
    "epd_4_in_2": (400, 300),
    "7_in_8": (1872, 1404),
    "epd_7_in_5_v3_colour": (880, 528),
    "epd_5_in_83": (600, 448),
    "image_file": (800, 480),
    "image_file_12_in_48": (1304, 984),
}


# Keep hardware-specific behavior keyed off the model registry instead of
# driver file names so new parallel displays can be added in one place.
parallel_display_models = {
    "7_in_8",
    "9_in_7",
    "10_in_3",
}


def is_parallel_display(model_name: str) -> bool:
    """Return True when the selected model uses a parallel display path."""
    return model_name in parallel_display_models
