import os
from PIL import Image, ExifTags


def rotate_image(infile):
    try:
        image = Image.open(r'/home/filipe/Pictures/TR-504-11.jpg')
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
        image.save(r'/home/filipe/Pictures/TR-504-11.jpg')
        image.close()

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass