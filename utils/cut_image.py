from PIL import Image
import os


class CutImage:
    def __init__(self, image, url):
        self.image = image
        self.url = url

    def resize(self):
        """
        缩小图片
        """
        im = Image.open(self.image)
        width, height = im.size

    def cut(self):
        # 制作缩略图
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
        small_name = 'small_' + os.path.basename(self.url)
        small_url = os.path.join(dir_name, small_name)
        small_region = region.resize((300, 300), Image.ANTIALIAS)
        small_region.save(small_url)
