import os, sys
import shutil
import asyncio

if "." not in sys.path :    sys.path.append(".")
from inkycal import Inkycal

CWD = os.getcwd()
IMAGE_FOLDER = f"{CWD}/image_folder"
SCRATCHPAD_DIR = os.path.abspath(os.path.dirname(__file__))
IMAGES_TO_ARCHIVE = ["frame_bw.png", "full-screen.png" ]

SETTINGS_PATHS = [
        { "label" : "no_border",    "settings_path" : f"{SCRATCHPAD_DIR}/settings_no_border.json"},
        { "label" : "border_0",     "settings_path" : f"{SCRATCHPAD_DIR}/settings_border_0.json"},
        { "label" : "border",       "settings_path" : f"{SCRATCHPAD_DIR}/settings_border.json"},
        { "label" : "180_border",   "settings_path" : f"{SCRATCHPAD_DIR}/settings_180_border.json"}
    ]

# remove images from previous runs
for png_file in [f for f in os.listdir(SCRATCHPAD_DIR) if f.endswith(".png")] :
    os.remove(f"{SCRATCHPAD_DIR}/{png_file}")

# save the full display qnd the visible frame for all settings.json above
for settings_info in SETTINGS_PATHS :
    label, settings_path = settings_info["label"], settings_info["settings_path"]

    inkycal = Inkycal(settings_path, render=True)
    asyncio.get_event_loop().run_until_complete( inkycal.run(run_once=True))

    # copy the rendered images to this folder
    for f in IMAGES_TO_ARCHIVE:
        shutil.copyfile(f"{IMAGE_FOLDER}/{f}", f"{SCRATCHPAD_DIR}/{label}_{f}")

    # print a bunch of data to check the settings.json is OK and the frame data makes sense
    print("##########################################################################")
    print(f"prefix '{label}' : ")
    print(f"Display :           size : {inkycal.Display.get_display_size(inkycal.settings['model'])}")
    if "frame_border_width_left" in inkycal.settings :
        print(f"Frame :             size : {inkycal.frame_size}")
        print(f"Frame :  frame_border_width_left : {inkycal.settings['frame_border_width_left']}, frame_border_height_top :{inkycal.settings['frame_border_height_top']}")
        print(f"      :  frame_border_width_right : {inkycal.settings['frame_border_width_right']}, frame_border_height_bottom :{inkycal.settings['frame_border_height_bottom']}")
        print(f"Frame :  corner 1 : {inkycal.frame_coord[0]:>3},{inkycal.frame_coord[1]:>3}")
        print(f"         corner 2 : {inkycal.frame_coord[2]:>3},{inkycal.frame_coord[3]:>3}")
    else :
        print(f"Frame :             no frame settings in the json ")
    
    total_module_height = 0
    for m in inkycal.settings['modules']:
        module_config = m["config"]
        module_info = f"size {str(module_config.get('size','n/a')):>10}\tpadding {module_config.get('padding_x','n/a'):>3},{module_config.get('padding_y','n/a'):>3}"
        total_module_height += module_config['size'][1]
        print(f"\tmodule {m['name']:<10} : {module_info}")

    print(f"\tmodule {'DEBUG':<10} : {inkycal.settings['info_section_height']} ({   inkycal.settings['info_section']})")
    print(f"total height : {total_module_height} (debug height:{inkycal.settings['info_section_height']})")

    
    print("##########################################################################")
