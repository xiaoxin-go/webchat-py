from PIL import Image
import os


class CutImage:
    def __init__(self, image, url):
        self.image = image
        self.url = url

    def cut(self):
        im = Image.open(self.image)
        width, height = im.size
        if width == height:
            return
        sub = abs(width - height) / 2
        if width > height:
            x = sub
            y = 0
            w = x + height
            h = height
        else:
            x = 0
            y = sub
            w = width
            h = y + width

        region = im.crop((x, y, w, h))
        dir_name = os.path.dirname(self.url)
        large_name = 'large_' + os.path.basename(self.url)
        large_url = os.path.join(dir_name, large_name)
        region.save(large_url)
        small_region = region.resize((300, 300), Image.ANTIALIAS)
        small_region.save(self.url)
