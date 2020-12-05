from inkycal.modules import *

# get list of all modules inside inkycal-modules folder
modules = [i for i in dir() if i[0].isupper()]

# Add the config of each module to the list settings
settings = []

for module in modules:
    command = f"conf = {module}.get_config()"
    exec(command)
    settings.append(conf)

# return the config of all modules for the web-ui
def get_all_config():
    return settings
