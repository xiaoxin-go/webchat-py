import os
import shutil

# 删除文件
if os.path.exists(r'app\templates\index.html'):
    os.remove(r'app\templates\index.html')

csses = r'app\static\css'
if os.path.exists(csses):
    shutil.rmtree(csses)

jses = r'app\static\js'
if os.path.exists(jses):
    shutil.rmtree(jses)

images = r'app\static\images'
if os.path.exists(images):
    shutil.rmtree(images)

# 复制文件
base_path = r'F:\web\webchat\dist'
index = r'%s\index.html' % base_path
shutil.copy(index, 'app/templates/index.html')

# 复制目录
src_css = r'%s\static\css' % base_path
shutil.copytree(src_css, csses)

src_js = r'%s\static\js' % base_path
shutil.copytree(src_js,jses)

src_images = r'%s\static\images' % base_path
shutil.copytree(src_images,images)

font = r'app\static\fonts'
src_font = r'%s\static\fonts' % base_path
shutil.copytree(src_font,font)

img = r'app\static\img'
src_img = r'%s\static\img' % base_path
shutil.copytree(src_img,img)



