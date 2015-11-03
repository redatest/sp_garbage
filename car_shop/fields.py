from django.db.models.fields.files import ImageField, ImageFieldFile
from PIL import Image
import os
from car_shop.python_iamge_watermark import markIt

# we use descriptors in this definition
# in the template file we get the thumbnail url like this: {{ item.image.thumb_url }}
def _add_thumb(s):
	"""  Modifies a sting containing an image filename to insert .thumb before the extension  """
	" s : is the file path of the imported image "

	parts = s.split(".")
	parts.insert(-1, "thumb")
	if parts[-1].lower() not in ['jpeg', 'jpg']:
		parts[-1] = 'jpg'

	path = '.'.join(parts)
	# add the appropriate dir to the original path
	path = add_dir(path, 'thumbnail')

	return path

def _add_marked(s):
	''' added marked to watermarked images '''

	parts = s.split(".")
	parts.insert(-1, "marked")  # insert marked before the last element
	if parts[-1].lower() not in ['jpeg', 'jpg']:
		parts[-1] = 'jpg'

	path = '.'.join(parts)
	# add the appropriate dir to the original path
	path = add_dir(path, 'marked')

	return path

def _add_big_marked(s):
	''' added marked to watermarked images '''

	parts = s.split(".")
	parts.insert(-1, "big_marked")  # insert marked before the last element
	if parts[-1].lower() not in ['jpeg', 'jpg']:
		parts[-1] = 'jpg'

	path = '.'.join(parts)
	# add the appropriate dir to the original path
	path = add_dir(path, 'big_marked')

	return path


def add_dir(str, opt):
	thepath = os.path.abspath(str)
	basepath = os.path.dirname(thepath)
	thefile = os.path.basename(thepath)
	return os.path.join(basepath, opt, thefile)

class ThumbnailImageFieldFile(ImageFieldFile):

	#################  used when saving the image as thumbnail in file storage
	def _get_thumb_path(self):
		return _add_thumb(self.path)

	thumb_path = property(_get_thumb_path)

	# used when getting the thumnail image url in the template file
	def _get_thumb_url(self):
		# title =  self.instance.title
		return _add_thumb(self.url)

	thumb_url = property(_get_thumb_url)

	#################  used when saving the thumb image as watermarked
	def _get_marked_path(self):
		return _add_marked(self.path)

	marked_path = property(_get_marked_path)

	# used when getting the watermarked image in the template
	def _get_marked_url(self):
		return _add_marked(self.url)

	marked_url = property(_get_marked_url)

	################## used when saving the original image as watermarked
	def _get_big_marked_path(self):
		return _add_big_marked(self.path)

	big_marked_path = property(_get_big_marked_path)

	# used when getting the watermarked image in the template
	def _get_big_marked_url(self):
		return _add_big_marked(self.url)

	big_marked_url = property(_get_big_marked_url)

	def save(self, name, content, save=True):
		super(ThumbnailImageFieldFile, self).save(name, content, save)

		img = Image.open(self.path)
		is_watermarked = False

		# save a thumbnail copy of the original in the file storage 
		nimage = img.resize((self.field.thumb_width, self.field.thumb_height), Image.ANTIALIAS )
		nimage.save(self.thumb_path, 'JPEG')

		# save a resized (600, 250) copy of the original in the file storage
		nimage = img.resize((600, 280), Image.ANTIALIAS )
		nimage.save(self.big_marked_path, 'JPEG')

		# test if watermarked field is checked
		is_watermarked = False
		
		if is_watermarked:
			# the original
			bwimage = markIt(self.big_marked_path)
			bwimage.save(self.big_marked_path, 'JPEG')
			
			# the thumbnail
			wimag = markIt(self.path)
			wimag.save(self.marked_path, 'JPEG')

	def delete(self, save=True):

		#  add test if watermarked or use self.path
		print 'deleting'

		print self.path
		print self.thumb_path

		if os.path.exists(self.thumb_path):
			print self.path
			print self.thumb_path

			os.remove(self.path)
			os.remove(self.thumb_path)
		super(ThumbnailImageFieldFile, self).delete(save)

class ThumbnailImageField(ImageField):
	attr_class = ThumbnailImageFieldFile

	def __init__(self, thumb_width=100, thumb_height=100, *args, **kwargs):

		self.thumb_width = thumb_width
		self.thumb_height = thumb_height
		super(ThumbnailImageField, self).__init__(*args, **kwargs)


	#   Edito:
	#  'name : header3.png  type: unicode'
	#  'self: photos/header3.png  type(self): <class 'app.fields.ThumbnailImageFieldFile'> '
	#  'self.path:  /home/enigma/django_projects/thumbnail_field/media/photos/header3.png  type unicode'
	#  'content:  photos/header3.png    type: <class 'app.fields.ThumbnailImageFieldFile'> '
	#  'self.field   <app.fields.ThumbnailImageField: image>'
