import io
from PIL import Image, ExifTags

from django.core.files.base import ContentFile


def rotate_image(infile):
    try:
        image = Image.open(infile)
        image_name = infile.name.rsplit('.', 1)[0]
        image_format = image.format

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)

        image_io = io.BytesIO()
        image.save(image_io, format=image_format)
        image = ContentFile(image_io.getvalue(), '{}.{}'.format(image_name, image_format))
        return image

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        return infile
