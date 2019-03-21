import os
import shutil

# 删除文件
if os.path.exists(r'app\templates\index.html'):
    os.remove(r'app\templates\index.html')

csses = r'app\static\css'
if os.path.exists(csses):
    shutil.rmtree(csses)


exclude_file = ['scripts.js', 'jquery-1.8.2.min.js']
jses = r'app\static\js'
if os.path.exists(jses):
    shutil.rmtree(jses)
#js_files = os.listdir(jses)
# for js_file in js_files:
#     if js_file in exclude_file:
#         continue
#     js_file_path = r'%s\%s' % (jses, js_file)
#     os.remove(js_file_path)

fonts = r'app\static\fonts'
if os.path.exists(fonts):
    shutil.rmtree(fonts)

images = r'app\static\images'
if os.path.exists(images):
    shutil.rmtree(images)

img = r'app\static\img'
if os.path.exists(img):
    shutil.rmtree(img)

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



