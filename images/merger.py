from PIL import Image
import numpy

module_name = 'inkycal_agenda'


def merge(module_name, out_filename):
  """Merge black pixels from image2 into image 1
  module_name = name of the module generating the image
  out_filename = what name to give to the finished file
  """
  
  im1_name, im2_name = module_name+'.png', module_name+'_colour.png'
  im1 = Image.open(im1_name).convert('RGBA')
  im2 = Image.open(im2_name).convert('RGBA')

  def clear_white(img):
    """Replace all white pixels from image with transparent pixels
    """
    x = numpy.asarray(img.convert('RGBA')).copy()
    x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(numpy.uint8)
    return Image.fromarray(x)

  im2 = clear_white(im2)
  im1.paste(im2, (0,0), im2)
  im1.save(out_filename+'.png', 'PNG')

merge(module_name, module_name+'2')


print('Done')
