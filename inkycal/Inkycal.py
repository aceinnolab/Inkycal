from inkycal.config import settings


f = '/home/pi/Desktop/settings.json'

settings = settings(f)

specified_modules = settings.active_modules()
for module in specified_modules:
  try:
    
    if module == 'inkycal_weather':
      from inkycal import weather
      conf = settings.get_config(module)
      weather = weather(conf['size'], conf['config'])

    if module == 'inkycal_rss':
      from inkycal import rss
      conf = settings.get_config(module)
      rss = rss(conf['size'], conf['config'])

    if module == 'inkycal_image':
      from inkycal import image
      conf = settings.get_config(module)
      image = image(conf['size'], conf['config'])

    if module == 'inkycal_calendar':
      from inkycal import calendar
      conf = settings.get_config(module)
      calendar = calendar(conf['size'], conf['config'])

    if module == 'inkycal_agenda':
      from inkycal import agenda
      conf = settings.get_config(module)
      agenda = agenda(conf['size'], conf['config'])

  except ImportError:
    print(
      'Could not find module: "{}". Please try to import manually.'.format(
      module))
