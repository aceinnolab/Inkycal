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


# Inkycal-setup
@app.route('/inkycal_config', methods=['GET', 'POST'])

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

        # template for basic settings
        template = {
            "model": model,
            "update_interval": update_interval,
            "orientation": int(request.form.get('orientation')),
            "info_section": info_section,
            "calibration_hours": [calibration_hour_1, calibration_hour_2, calibration_hour_3],
            "modules": [],
            }

        # common module config (shared by all modules)
        padding_x = int(request.form.get('padding_x'))
        padding_y = int(request.form.get('padding_y'))
        fontsize = int(request.form.get('fontsize'))
        language = request.form.get('language')

        common_settings = {'padding_x':padding_x, 'padding_y':padding_y, 'fontsize':fontsize, 'language':language}

        # display size
        display_size = Display.get_display_size(model)
        width, height = int(display_size[0]), int(display_size[1])
        

        # loop over the modules, add their config data based on user selection, merge the common_settings into each module's config
        for i in range(1,4):
            conf = {}
            module = 'module'+str(i)
            if request.form.get(module) != "None":

                conf = {"position":i , "name": request.form.get(module), "config":{}}

                for modules in settings:
                    if modules['name'] == request.form.get(module):

                        conf['config']['size'] = (width, int(height*int(request.form.get(module+'_height')) /100))

                        # Add required fields to the config of the module in question
                        if 'requires' in modules:
                            for key in modules['requires']:
                                conf['config'][key] = request.form.get(module+'_'+key).replace(" ", "")

                        # For optional fields, check if user entered/selected something. If not, and a default value was given,
                        # use the default value, else set the value of that optional key as None
                        if 'optional' in modules:
                            for key in modules['optional']:
                                if request.form.get(module+'_'+key):
                                    conf['config'][key] = request.form.get(module+'_'+key).replace(" ", "")
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
            user_settings = json.dumps(template, indent=4).replace('null', '""').encode('utf-8')
            response = Response(user_settings, mimetype="application/json", direct_passthrough=True)
            response.headers['Content-Disposition'] = 'attachment; filename=settings.json'

            return response
            # redirect('/index')

        except Exception as e:
            flash(str(e))

    return render_template('inkycal_config.html', title='Inkycal-Setup', conf=settings, form=form)
