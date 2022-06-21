"""
DOCSTRING

"""
import os
from flask import Flask, flash, redirect, send_from_directory, jsonify, request

from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import numpy as np
import scipy.misc
import cv2
import time
from . import routes
import image_utils as iu
import ast
from os.path import basename, splitext

SIZE = 500, 500
UPLOAD_FOLDER_EDGE = './uploads'
FULLSIZE_FOLDER_EDGE = './uploads/fullsize'
THUMB_FOLDER_EDGE = './uploads/thumb'

app = Flask(__name__)
app.config['UPLOAD_FOLDER_EDGE'] = UPLOAD_FOLDER_EDGE
app.config['FULLSIZE_FOLDER_EDGE'] = FULLSIZE_FOLDER_EDGE
app.config['THUMB_FOLDER_EDGE'] = THUMB_FOLDER_EDGE


@routes.route('/cmaps', methods=['GET'])
def cmaps():
    return jsonify(iu.CATEGORIZED_COLORMAPS)

@routes.route('/uploads/<path:path>', methods=['GET'])
def view_edge_images(path):
    return send_from_directory('../uploads/', path)


@routes.route('/upload', methods=['POST'])
def upload_edge_file():
    files = request.files.getlist("file[]")
    colors = ast.literal_eval(request.form["colors"])
    final_json = { 'props':[], 'merged_image':'', 'merged_contour':'' }
    detection_method = request.args.get('dm')
    cmap = request.args.get('cm')
    color_mask = request.args.get('crmk')
    
    if detection_method is None:
        return jsonify({'msg':'Detection method is required'}), 400
    
    contours = []
    segmentations = []
    thumbs = []
    
    for idx, f in enumerate(files):
        if f.filename == '':
            return redirect(request.url)
        if f is None or not iu.valid_image_extensions(f.filename):
            flash('No selected file')
            return redirect(request.url)

        thumb, _ = iu.save_and_resize(f, app.config['FULLSIZE_FOLDER_EDGE'], app.config['THUMB_FOLDER_EDGE'])

        if color_mask and color_mask != 'undefined':
            iu.color_mask(thumb, color_mask)

        if cmap:
            iu.colorize(thumb, cmap=cmap)

        try:
            if detection_method == 'contour':
                prop, segmentation,  image_contour = detect_contours(thumb, f.filename, request.args, colors[idx])
            elif detection_method == 'circle':
                prop, segmentation, image_contour = detect_circle(thumb, f.filename, request.args, colors[idx])
        except AttributeError as detail:
            print(detail)
            return jsonify({'msg': "No %s found with these parameters" % (detection_method)  }), 400

        final_json['props'].append(prop)
        
        fname, fextension = splitext(f.filename)

        thumbs.append({'path':thumb, 'name': fname + '_original' + fextension })
        segmentations.append({'path':segmentation, 'name': fname + '_segmentation' + fextension })
        contours.append({'path':image_contour, 'name':fname + '_contour' + fextension })   

    if len(files) > 1:
        final_json['original'] = iu.merge_images(thumbs, './uploads/modified/')
        final_json['segmentation'] = iu.merge_images(segmentations, './uploads/modified/', enhance=False)
        final_json['contour'] = iu.merge_images(contours, './uploads/modified/', enhance=False)
    else:
        final_json['original'] = thumb
        final_json['segmentation'] = segmentation
        final_json['contour'] = image_contour
    return jsonify(final_json)

def detect_circle(fpath, filename, opts, color=(255,0,0)):

    low_thresh = opts.get('lt', 50,type=int)
    high_thresh = opts.get('ht', 125,type=int)
    min_distance = opts.get('md', 5,type=int)
    min_radius = opts.get('mr', 5,type=int)
    denoise = opts.get('d', 5,type=int)
    denoise = denoise if denoise % 2 == 1 else denoise + 1
    max_radius = opts.get('mar', 50,type=int)

    img = cv2.imread(fpath)
    img = cv2.medianBlur(img,denoise)
    
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cimg = cv2.cvtColor(gray_img,cv2.COLOR_GRAY2BGR)
    circles = cv2.HoughCircles(gray_img,cv2.HOUGH_GRADIENT,1,min_distance, param1=low_thresh,param2=high_thresh,minRadius=min_radius,maxRadius=max_radius)
    if circles is None:
        pass
    else: 
        circles = np.uint16(np.around(circles))

        for i in circles[0,:]:
            cv2.circle(cimg,(i[0],i[1]),i[2],color,2)
            cv2.circle(cimg,(i[0],i[1]),2,(0,0,255),3)


    cv2.imwrite('./uploads/modified/circle_big' + basename(fpath), cimg)
    
    ret = {}
    ret['name'] = filename
    ret['original'] = '/uploads/thumb/' + basename(fpath)
    ret['modified'] = '/uploads/modified/'+ basename(fpath)
    ret['big'] = '/uploads/modified/circle_big' + basename(fpath)
    ret['results'] = 0 if circles is None else len(circles[0,:])
    return ret, './uploads/modified/' + basename(fpath), './uploads/modified/circle_big' + basename(fpath)


def detect_contours(fpath, filename, opts, color=(255,0,0)):
    
    denoise = opts.get('d', 0, type=int)
    # max_arc_length = opts.get('mal', 10, type=int)
    low_thresh = opts.get('lt', 50,type=int)
    high_thresh = opts.get('ht', 125,type=int)
    n_iters = opts.get('ni', 2,type=int)
    min_area = opts.get('ma', 5,type=int)
    max_area = opts.get('maa', 50,type=int)

    #CRIANDO UMA MATRIZ ZERADA PARA OS PIXELS COM CONTORNO VERDE
    big = np.zeros((SIZE), np.uint8)
    #CRIANDO UMA MATRIZ ZERADA PARA OS PIXELS COM CONTORNO BRANCO
    all = np.zeros((SIZE), np.uint8)
    #CRIANDO UMA MATRIZ ZERADA PARA OS PIXELS COM CONTORNO BRANCO
    nova = np.zeros((SIZE), np.uint8)
    
    img = cv2.imread(fpath)

    if denoise > 0:
        img = cv2.fastNlMeansDenoisingColored(img, None, denoise,10,7,21)
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _,alpha = cv2.threshold(tmp,5,255,cv2.THRESH_BINARY)
    # b, g, r = cv2.split(img)
    # rgba = [b,g,r, alpha]
    # img = cv2.merge(rgba,4)
    _, img = cv2.threshold(img,200,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    im_canny = img.copy()
    im_canny = cv2.Canny(im_canny, low_thresh, high_thresh)
    if n_iters > 0:
        kernel = np.ones((2,2),np.uint8)
        im_canny = cv2.dilate(im_canny,kernel,iterations = n_iters)
    contours, hierarchy = cv2.findContours(im_canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    big = cv2.cvtColor(big,cv2.COLOR_GRAY2RGB)
    dot_count = 0
    lineType = 8
    maxLevel = 0
    thickness = 1

    for i, c in enumerate(contours):
        contour_area = cv2.contourArea(c, True)
        if contour_area <= max_area:
            continue
        moments = cv2.moments(c)
        cgx = int(moments['m10']/moments['m00'])
        cgy = int(moments['m01']/moments['m00'])

        (x,y),radius = cv2.minEnclosingCircle(c)
        center = (int(x),int(y))
        # radius = int(radius)
        # cv2.circle(big,center,radius,(0,0,255),2)
        cv2.circle(big,center,2,(0,0,255),3)
        # cv2.line(big, (cgx -5,cgy), (cgx + 5,cgy), (255,255,255) ,1)
        # cv2.line(big, (cgx,cgy - 5), (cgx,cgy +5), (255,255,255) ,1)
        dot_count += 1
    
    cv2.drawContours(big, contours, -1, color ,1 )
    # cv2.drawContours(all, contours, -1, (255 ,255 ,255) ,1)
    # cv2.imwrite('./uploads/modified/contour_' + basename(fpath), all)
    cv2.imwrite('./uploads/modified/contour_big' + basename(fpath), big)
    cv2.imwrite( './uploads/modified/' + basename(fpath), img)


    # img = cv2.imread('./uploads/modified/' + basename(fpath), 0)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    # img = clahe.apply(img)
    # cv2.imwrite( './uploads/modified/' + basename(fpath), img)

    ret = {}
    ret['name'] = filename
    ret['original'] = '/uploads/thumb/' + basename(fpath)
    ret['modified'] = '/uploads/modified/' + basename(fpath)
    ret['big'] = '/uploads/modified/contour_big' + basename(fpath)
    ret['results'] = dot_count
    return ret, './uploads/modified/' + basename(fpath),  './uploads/modified/contour_big' + basename(fpath)

