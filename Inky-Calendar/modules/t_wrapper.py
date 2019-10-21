from configuration import *
from settings import *

"""
def wrapper(text, font=default, max_width = display_width):
  counter = 0
  padding = 50
  lines = []
  if font.getsize(text)[0] < max_width:
    lines.append(text)
  else:
    for i in range(1, len(text.split())+1):
      line = ' '.join(text.split()[counter:i])
      if not font.getsize(line)[0] < max_width- padding:
        lines.append(line)
        line = ''
        counter = i
      if i == len(text.split()) and line != '':
        lines.append(line)
  return lines
"""

def text_wrap(text, font=default, line_width = display_width):
  counter, lines = 0, []
  if font.getsize(text)[0] < line_width:
    lines.append(text)
  else:
    while font.getsize(text)[0] < line_width:
      
    """
    for i in range(1, len(text.split())+1):
      line = ' '.join(text.split()[counter:i])
      print(line, font.getsize(line)[0])
    """
  
#text  = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'

#text = 'Russia submersible fire was in battery compartment Fourteen crew died in the fire on board'

text = "Russian LGBT activist Yelena Grigoryeva murdered in St Petersburg: Yelena Grigoryeva, 41, was stabbed and strangled near her home in St Petersburg, relatives say."

lines = text_wrap(text, default, display_width)

line = len(max(lines, key=len))

for i in lines:
  print(i, ' ' * (line-len(i)),'| width: ',default.getsize(i)[0])
  
