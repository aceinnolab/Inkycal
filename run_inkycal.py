from inkycal import Inkycal

"""
    # If your settings.json file is not in /boot, use the full path:
inky = Inkycal('path/to/settings.json', render=True)
     
    # Test if Inkycal can be run correctly, running this will show a bit of info for each module
inky.test() 
 
    # If there were no issues, you can run Inkycal nonstop
inky.run()
"""
inky = Inkycal(render=False)

#inky.test()
inky.run()
