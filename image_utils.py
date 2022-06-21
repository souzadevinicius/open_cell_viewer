import os 
import string
from PIL import Image
from werkzeug.utils import secure_filename
from skimage.filters import rank, threshold_otsu
from skimage.morphology import disk
import numpy as np
import cv2
from matplotlib import pyplot as plt

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def validate_image_upload(file, redirect, request, flash):
    if file.filename == '':
        return redirect(request.url)
    if file is None or not valid_image_extensions(file.filename):
        flash('No selected file')
        return redirect(request.url)

def resize_image(fpath, filename, folder, size=(500,500)):
    outfile = os.path.join(folder, filename.rsplit('.', 1)[0] + '_thumb.' + 'png')
    im = Image.open(fpath)
    im = im.resize(size, Image.ANTIALIAS).convert("RGBA")

    # data = np.array(im)   # "data" is a height x width x 4 numpy array
    # red, green, blue, alpha = data.T # Temporarily unpack the bands for readability

    # # Replace white with red... (leaves alpha values alone...)
    # white_areas = (red == 255) & (blue == 255) & (green == 255)
    # data[...][white_areas.T] = (0, 0, 0, 0) # Transpose back needed

    # im = Image.fromarray(data)


    im.save(outfile, 'PNG')
    return outfile, im

# def save_and_resize(file, fullsize_path, thumb_path ):
#     filename = secure_filename(file.filename)
#     fpath = os.path.join(fullsize_path, filename)
#     file.save(fpath)
#     return resize_image(fpath, filename, thumb_path)

def save_and_resize(file, fullsize_path, thumb_path ):
    filename = secure_filename(file.filename)
    fpath = os.path.join(fullsize_path, filename)
    file.save(fpath)
    return resize_image(fpath, filename, thumb_path)

# def merge_images(files, fullsize_folder, thumb_folder, dest_folder, enhance=False):
#     print(files,'fiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiles')
#     for idx, f in enumerate(files):
#         if idx == 0:
#             fpath, _ = save_and_resize(files[0], fullsize_folder, thumb_folder)
#             fpath2, _ = save_and_resize(files[1], fullsize_folder, thumb_folder)
#             final_name = dest_folder + os.path.basename(f.filename)
#         elif idx == 1:
#             continue
#         elif idx > 1:
#             fpath = final_name
#             fpath2, _ = save_and_resize(f, fullsize_folder, thumb_folder)
#         im1 = Image.open(fpath).convert('RGBA')
#         im2 = Image.open(fpath2).convert('RGBA')
#         alpha = 0.5 if idx != len(files) -1 else 0.2
#         blend = Image.blend(im1, im2, alpha)
#         blend.save(final_name, 'PNG')

#         print(enhance)
#         if enhance:
#           img = cv2.imread(final_name)
#           img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
#           # equalize the histogram of the Y channel
#           img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
#           # convert the YUV image back to RGB format
#           img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
#           cv2.imwrite(final_name, img_output)

#     return final_name

def merge_images(files, dest_folder, enhance=False):
    for idx, f in enumerate(files):
        if idx == 0:
            fpath = files[0]['path']
            fpath2 = files[1]['path']
            final_name = dest_folder + os.path.basename(f['name'])
        if idx == 1:
            continue
        if idx > 1:
            fpath = final_name
            fpath2 = f['path']
        im1 = Image.open(fpath).convert('RGBA')
        im2 = Image.open(fpath2).convert('RGBA')
        alpha = 0.5 if idx != len(files) -1 else 0.2
        blend = Image.blend(im1, im2, alpha)
        blend.save(final_name, 'PNG')
        if enhance:
          img = cv2.imread(final_name)

          img_output = equalize_hist(img)

          # img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
          # # equalize the histogram of the Y channel
          # img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
          # # convert the YUV image back to RGB format
          # img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
          cv2.imwrite(final_name, img_output)
    return final_name

def equalize_hist(img):
    for c in range(0, 2):
       img[:, :, c] = cv2.equalizeHist(img[:, :, c])
    return img

def valid_image_extensions(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


CATEGORIZED_COLORMAPS = [('Perceptually Uniform Sequential', [
            'viridis', 'plasma', 'inferno', 'magma']),
         ('Sequential', [
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
         ('Sequential (2)', [
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper']),
         ('Diverging', [
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
         ('Qualitative', [
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c']),
         ('Miscellaneous', [
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar'])]

COLORMAPS = [  'viridis', 'plasma', 'inferno', 'magma',
            'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
            'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
            'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn',
            'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
            'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
            'hot', 'afmhot', 'gist_heat', 'copper',
            'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
            'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
            'Pastel1', 'Pastel2', 'Paired', 'Accent',
            'Dark2', 'Set1', 'Set2', 'Set3',
            'tab10', 'tab20', 'tab20b', 'tab20c',
            'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
            'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg', 'hsv',
            'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar']

def colorize(file,dest_folder=None,cmap='binary',denoise=5, gradient=0):
    if cmap not in COLORMAPS:
      return cv2.imread(file)
    img = cv2.imread(file, 0)

    
    img = rank.median(img, disk(denoise))
    if gradient > 0:
      img = rank.gradient(img, disk(5))
    # val = threshold_otsu(img)
    # gradient = img < val
    dst = file if dest_folder is None else dest_folder 
    plt.imsave(dst, np.array(img), cmap=cmap)
    return cv2.imread(dst)

def color_mask(file,lower_range, upper_range=[255,255,255]):
    img = cv2.imread(file)
    if isinstance(lower_range, str):
        lower_range = lower_range.replace('(','').replace(')','').replace('rgb','').split(',')
        lower_range = tuple(list(map(int, lower_range)))
        upper_range = tuple(list(map(int, upper_range)))

    print(type(lower_range))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img = cv2.inRange(hsv, lower_range, upper_range)
    # img = cv2.bitwise_and(img, img, mask=mask)
    plt.imsave(file, np.array(img))
    return cv2.imread(file)
    
