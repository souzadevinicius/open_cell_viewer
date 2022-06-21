import os
import pickle
from flask import Flask, flash, redirect, send_from_directory, jsonify, request
import image_utils as iu
from . import routes
import logging
from scipy import misc
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import linear_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER_TRAIN = './train'
UPLOAD_FOLDER_PREDICT = './predict'
FULLSIZE_FOLDER_TRAIN = './train/fullsize'
FULLSIZE_FOLDER_PREDICT = './predict/fullsize'
THUMB_FOLDER_TRAIN = './train/thumb'
THUMB_FOLDER_PREDICT = './predict/thumb'
MODEL_FILE_NAME = 'model.pkl'

app = Flask(__name__)
app.config['UPLOAD_FOLDER_TRAIN'] = UPLOAD_FOLDER_TRAIN
app.config['FULLSIZE_FOLDER_TRAIN'] = FULLSIZE_FOLDER_TRAIN
app.config['THUMB_FOLDER_TRAIN'] = THUMB_FOLDER_TRAIN

app.config['UPLOAD_FOLDER_PREDICT'] = UPLOAD_FOLDER_PREDICT
app.config['FULLSIZE_FOLDER_PREDICT'] = FULLSIZE_FOLDER_PREDICT
app.config['THUMB_FOLDER_PREDICT'] = THUMB_FOLDER_PREDICT

@routes.route('/train', defaults={'path': ''})
@routes.route('/train/<path:path>', methods=['GET'])
def view_train_images(path):
    if os.path.isfile( os.path.join(os.getcwd(), UPLOAD_FOLDER_TRAIN, path) ):
        return send_from_directory((os.path.join(os.getcwd(), UPLOAD_FOLDER_TRAIN)), path)
    files_json = []
    for subdir, dirs, files in os.walk( os.path.join(os.getcwd(), UPLOAD_FOLDER_TRAIN, path) ):
        subdir = subdir.replace('\\','/')
        [ files_json.append({'name': f, 'path': '/'.join( [ UPLOAD_FOLDER_TRAIN[1:], subdir.rsplit('/', 1)[1], f] ) }) for f in files if iu.valid_image_extensions(f) ]
    return jsonify(files_json)

@routes.route('/train/images', methods=['POST'])
def upload_train_file():
    files = request.files.getlist("train[]")
    for idx, f in enumerate(files):
        iu.validate_image_upload(f, redirect, request, flash)
        f.filename = '{0}_{1}{2}'.format(request.args.get("n").replace("_", "") , idx, os.path.splitext(f.filename)[1] )
        thumb, _ = iu.save_and_resize(f, app.config['FULLSIZE_FOLDER_TRAIN'], app.config['THUMB_FOLDER_TRAIN'])
        cmap = request.args.get('cm')
        if cmap in iu.COLORMAPS:
          iu.colorize(thumb, cmap=cmap)
    return "OK", 200

@routes.route('/predict', methods=['POST'])
def predict():
    files = request.files.getlist("predict[]")
    images_predict = []
    for idx, f in enumerate(files):
        iu.validate_image_upload(f,redirect,request, flash)
        thumb, _ = iu.save_and_resize(f, app.config['FULLSIZE_FOLDER_PREDICT'], app.config['THUMB_FOLDER_PREDICT'])
        cmap = request.args.get('cm')
        if cmap in iu.COLORMAPS:
          iu.colorize(thumb, cmap=cmap)
        image = misc.imread(thumb, mode='P')
        images_predict.append(image.flatten())

    model_file = os.path.join(os.getcwd(), MODEL_FILE_NAME)

    if not os.path.exists(model_file):
       return jsonify({'msg':'You must train before predict'}), 400
 
    clf = pickle.load(model_file)
    logger.info('Realizando predicoes')
    pre = clf.predict(images_predict)
    return jsonify(pre[0])

@routes.route('/train', methods=['POST'])
def train_route():
    clf = classifier()
    model_file = os.path.join(os.getcwd(), MODEL_FILE_NAME)
    pickle.dump(clf, model_file)
    return jsonify({'msg':'Trained'}), 200



def classifier(data=None, target=None):
    clf = linear_model.SGDClassifier(alpha=0.0001, average=False, class_weight=None, epsilon=0.1,
       eta0=0.0, fit_intercept=True, l1_ratio=0.15,
       learning_rate='optimal', loss='modified_huber', max_iter=10,
       n_jobs=-1, penalty='l2', power_t=0.5, random_state=None,
       shuffle=True, tol=None, verbose=1, warm_start=False)
    if not data or not target: 
        data, target = data_and_target()
    clf.fit(data, target)
    return clf

def data_and_target():
    target = []
    data = []
    for subdir, _, files in os.walk(app.config['THUMB_FOLDER_TRAIN']):
        for filename in files:
            image = misc.imread(os.path.join(os.getcwd(), subdir, filename), mode='P')
            data.append(image.flatten())
            target.append(filename.split('_')[0])
    return data, target

@routes.route('/accuracy', methods=['GET'])
def accuracy_route():
    data, target = data_and_target()
    X_train, X_test, y_train, y_test = train_test_split(data, target, test_size=0.33, random_state=42)
    clf = classifier(X_train, y_train)
    accuracy = clf.score(X_test, y_test)
    return jsonify({'msg': 'Accuracy:' +  str(accuracy) })



def read_images(path, targs, is_train=False, saturate=True):
    """Iterate through train and predict folders searching for images"""
    logger.info("Lendo as imagens de {}  :) ".format('treino' if is_train else 'previsao'))
