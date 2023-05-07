from flask import Flask, request, jsonify
from flask import send_from_directory
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import binascii
import Utility
import Constants
import logging
import base64
import keras
import time
# for Tensorflow JS
import tensorflowjs as tfjs
import requests
import urllib


app = Flask(__name__)
logger_level_set = False

@app.route('/', methods=['GET'])
def root_handler():
    if logger_level_set == False:
        app.logger.setLevel(logging.ERROR)
        return "For Your Keys Only!"

@app.route('/get_ann', methods=['POST'])
def get_ann():
    
    content_type_invalid_check = Utility.is_content_type_not_json(request=request)
    if content_type_invalid_check != None:
        return content_type_invalid_check, 400
    
    json = request.json
    logging.log(msg='request json='+str(json), level=logging.ERROR)
    format = Constants.H5
    format = json.get(Constants.FORMAT)
    if (format != Constants.H5) and (format != Constants.TFJS):
        format = Constants.H5

    # TFJS Models are created in a directory with model.json along with .bin files representing model weights
    # This application would create the TFJS model directory and share the directory name with the Client
    # Client has load the model by appending model.json to the URL to further fetch the .bin files from the same
    # directory
    if format == Constants.TFJS:
        model = Utility.generate_ANN(use_complex_model=False)
        model_folder_path = Utility.save_model(model=model, format=format, is_complex=False,  model_folder_path='/models/')
        model_folder = Utility.os.path.basename(model_folder_path).split('/')[-1]
        return Utility.compose_get_ann_response(model_file_path=model_folder, format=format, is_encrypted=False,ann_id=model_folder_path)
    elif format == Constants.H5:
        model_to_share = ''
        directory = '.'
        aes_key_encrypted_base64 = Constants.NA
        model = Utility.generate_ANN(use_complex_model=False)
        model_file_path = Utility.save_model(model=model, format=format, is_complex=False,  model_folder_path='/models/')
        logging.log(msg='model_file_path='+model_file_path, level=logging.ERROR)
        is_encrypted = True
        if json.get(Constants.RSA_PUBLIC_KEY_2048_BASE64) != 'None':
            public_key_pem = base64.b64decode(json.get(Constants.RSA_PUBLIC_KEY_2048_BASE64))
            public_key = RSA.import_key(public_key_pem)
            rsa_pub_key_base64 = base64.b64encode(public_key.export_key()).decode("ascii")
            model_file_encrypted_path, aes_key_encrypted_base64 = Utility.encrypt_model(model_file_path=model_file_path, rsa_public_key=public_key, format='h5')
            logging.log(msg='model_file_encrypted_path='+model_file_encrypted_path, level=logging.ERROR)
            logging.log(msg='aes_key_encrypted_base64='+aes_key_encrypted_base64, level=logging.ERROR)
            encrypted_model_name = Utility.os.path.basename(model_file_encrypted_path).split('/')[-1]
            model_to_share = encrypted_model_name
            model_file_path = model_file_encrypted_path
        else:
            is_encrypted = False
            model_to_share = Utility.os.path.basename(model_file_path).split('/')[-1]
        directory = Utility.os.path.dirname(model_file_path)
        logging.log(msg='model_to_share='+model_to_share, level=logging.ERROR)
        logging.log(msg='directory='+directory, level=logging.ERROR)
        return Utility.compose_get_ann_response(model_file_path=model_file_encrypted_path, format=format, is_encrypted=is_encrypted,ann_id=model_to_share, aes_key_encrypted_base64=aes_key_encrypted_base64)

@app.route('/send_message', methods=['POST'])
def handle_encrypted_request():

    content_type_invalid_check = Utility.is_content_type_not_json(request=request)
    if content_type_invalid_check != None:
        return content_type_invalid_check, 400
    
    json = request.json
    logging.log(msg='request json='+str(json), level=logging.ERROR)
    
    format = json.get(Constants.FORMAT)
    if (format != Constants.H5) and (format != Constants.TFJS):
        format = Constants.H5
    is_message_uri_encoded = json.get(Constants.IS_MESSAGE_URI_ENCODED)
    enc_message = json.get(Constants.ENCRYPTED_MESSAGE)
    utc_time_seconds = json.get(Constants.UTC_TIME_SECONDS)
    random_string = json.get(Constants.RANDOM_STRING)
    ann_id = json.get(Constants.ANN_ID)
    if (enc_message == None) or (utc_time_seconds == None) or (random_string == None):
        err_msg = f'Invalid or missing inputs'
        return Utility.get_error_json(err_msg), 400
    
    # replay attack case: reject requests reaching beyond tolerance window of utc time in seconds
    current_utc_time = int(time.time())
    min_utc_time = current_utc_time - Constants.UTC_TIME_TOLERANCE
    max_utc_time = current_utc_time + Constants.UTC_TIME_TOLERANCE
    if utc_time_seconds < min_utc_time:
        err_msg = f'Stale Request: Rejecting it'
        return Utility.get_error_json(err_msg), 401
    if utc_time_seconds > max_utc_time:
        err_msg = f'Request from the future: Rejecting it'
        return Utility.get_error_json(err_msg), 401
    
    model_folder_path = "./models/"
    if ann_id.endswith('.encrypted'):
        ann_id = ann_id[0: len(ann_id) - len('.encrypted')]
    model_file_path = model_folder_path + ann_id
    if format == Constants.H5:
        model = keras.models.load_model(model_file_path)
    elif format == Constants.TFJS:
        model= tfjs.converters.load_keras_model(model_file_path+'/model.json')

    aes_key,_,_,_ = Utility.generate_aes_key(model, random_string=random_string, utc_time=str(utc_time_seconds))
    message_in_request, success = Utility.decrypt_message_with_aes_key(encrypted_message=enc_message, aes_key=aes_key)
    if success:
        if is_message_uri_encoded == True:
            message_in_request = urllib.parse.unquote(message_in_request)
        logging.log(msg='message_in_request='+message_in_request, level=logging.ERROR)
        response_json = {
            "request_message":message_in_request
        }
        return jsonify(response_json)
    else:
        response_json = {
            "request_message":message_in_request
        }
        return jsonify(response_json), 400

# path to fetch html page which inturn loads FYKO.js file which uses Tensorflowjs to load and use ANN models
@app.route('/tfjs/FYKO_JS/<file_name>', methods=['GET'])
def get_tfjs_client(file_name):
    directory = './FYKO_JS'
    return send_from_directory(directory=directory, path=file_name)

# path to fetch model json for Tensorflowjs (tfjs) clients which are Javascript based meant for browser apps
@app.route('/tfjs/<model_name>/<model_file>', methods=['GET'])
def get_tfjs_ann(model_name, model_file):
    directory = './models/'+model_name
    return send_from_directory(directory=directory, path=model_file)

# path to fetch JSZip file for Tensorflow js
@app.route('/jszip', methods=['GET'])
def get_jszip():
    return send_from_directory(directory=Constants.JSZIP_DIRECTORY, path=Constants.JSZIP_JS_FILE)

if (__name__ == '__main__'):
    app.run(port=8000)