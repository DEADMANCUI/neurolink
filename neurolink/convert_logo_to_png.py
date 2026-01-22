from PIL import Image
import os
base = os.path.dirname(__file__)
src = os.path.join(base, 'assets', 'logo.jpeg')
dst = os.path.join(base, 'assets', 'logo.png')
img = Image.open(src)
img.save(dst, format='PNG')
print('saved', dst)
