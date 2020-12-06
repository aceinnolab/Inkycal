from flask import render_template, flash, redirect, request, Response
from app import app
from app.forms import LoginForm
import json

from inkycal import Display

from .config_loader import get_all_config

settings = get_all_config()

# Home
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

# Wifi-setup
@app.route('/setup_wifi')
def wifi_setup():
    return render_template('wifi.html', title='Wifi-setup')

# SSH file
@app.route('/create_ssh')
def create_ssh():
    return render_template('create_ssh.html', title='SSH file generator')


# Inkycal-setup
@app.route('/inkycal-config-v2-0-0', methods=['GET', 'POST'])

def inkycal_config():
    form = LoginForm()
    if form.validate_on_submit():

        # General epaper settings
        model = request.form.get('model')
        update_interval = int(request.form.get('update_interval'))
        calibration_hour_1 = int(request.form.get('calibration_hour_1'))
        calibration_hour_2 = int(request.form.get('calibration_hour_2'))
        calibration_hour_3 = int(request.form.get('calibration_hour_3'))
        orientation: int(request.form.get('orientation'))
        language = request.form.get('language')
        info_section = True if (request.form.get('info_section') == "on") else False

        info_height = int(request.form.get('info_section_height')) if info_section == True else None

        # template for basic settings
        template = {
            "model": model,
            "update_interval": update_interval,
            "orientation": int(request.form.get('orientation')),
            "info_section": info_section,
            "info_section_height": info_height,
            "calibration_hours": [calibration_hour_1, calibration_hour_2, calibration_hour_3],
            "modules": [],
            }


        # common module config (shared by all modules)
        padding_x = int(request.form.get('padding_x'))
        padding_y = int(request.form.get('padding_y'))
        fontsize = int(request.form.get('fontsize'))
        language = request.form.get('language')

        common_settings = {"padding_x":padding_x, "padding_y":padding_y, "fontsize":fontsize, "language":language}

        # loop over the modules, add their config data based on user selection, merge the common_settings into each module's config
        no_of_modules = int(request.form.get("module_counter"))

        # display size ---- Since Inkycal works in vertical mode (only), the width and height have to be flipped here
        display_size = Display.get_display_size(model) # returns width,height but flipping these for vertical mode
        height, width = int(display_size[0]), int(display_size[1])

        # If info section was active, substract the height of the info section from the display height
        if info_section == True:
            height = height-info_height

        # get all module heights, calculate single part
        module_sizes = [int(request.form.get(f"module{i}_height")) for i in range(1, no_of_modules+1)]

        if sum(module_sizes) != 0:
            single_part = height / sum(module_sizes)

        for i in range(1, no_of_modules+1):
            conf = {}
            module = 'selected_module'+str(i)

            if request.form.get(module) != "None":
                conf = {"position":i , "name": request.form.get(module), "config":{}}

                for modules in settings:
                    if modules['name'] == request.form.get(module):

                        module_height = int( request.form.get(f"module{i}_height") )
                        conf['config']['size'] = (width, int(single_part*module_height) )

                        # Add required fields to the config of the module in question
                        # True/False choices are converted to string for some reason, leading to incorrect values
                        # Convert "True" to True, "False" to False and empty input to None
                        if 'requires' in modules:
                            for key in modules['requires']:
                                val = request.form.get(f'module{i}_{key}').replace(" ", "")
                                if val == "True":
                                    val = True
                                elif val == "False":
                                    val = False
                                elif val == "":
                                        val = None
                                conf['config'][key] = val

                        # For optional fields, check if user entered/selected something. If not, and a default value was given,
                        # use the default value, else set the value of that optional key as None
                        # True/False choices are converted to string for some reason, leading to incorrect values
                        # Convert "True" to True, "False" to False and empty input to None
                        if 'optional' in modules:
                            for key in modules['optional']:
                                if request.form.get(f'module{i}_{key}'):
                                    val = request.form.get(f'module{i}_{key}').replace(" ", "")
                                    if val == "True":
                                        val = True
                                    elif val == "False":
                                        val = False
                                    elif val == "":
                                        val = None
                                    conf['config'][key] = val
                                else:
                                    if "default" in modules["optional"][key]:
                                        conf['config'][key] = modules["optional"][key]["default"]
                                    else:
                                        conf['config'][key] = None

                # update the config dictionary
                conf["config"].update(common_settings)
                template['modules'].append(conf)

        # Send the data back to the server side in json dumps and convert the response to a downloadable settings.json file
        try:
            user_settings = json.dumps(template, indent=4).encode('utf-8')
            response = Response(user_settings, mimetype="application/json", direct_passthrough=True)
            response.headers['Content-Disposition'] = 'attachment; filename=settings.json'

            return response

        except Exception as e:
            flash(str(e))


    return render_template('inkycal-config-v2-0-0.html', title='Inkycal-Setup', conf=settings, form=form)

