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
    return Utility.compose_get_ann_response(model_file_path=model_file_encrypted_path, is_encrypted=is_encrypted,ann_id=model_to_share, aes_key_encrypted_base64=aes_key_encrypted_base64)

@app.route('/send_message', methods=['POST'])
def handle_encrypted_request():

    content_type_invalid_check = Utility.is_content_type_not_json(request=request)
    if content_type_invalid_check != None:
        return content_type_invalid_check, 400
    
    json = request.json
    logging.log(msg='request json='+str(json), level=logging.ERROR)
    
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
    model = keras.models.load_model(model_file_path)
    aes_key,_,_,_ = Utility.generate_aes_key(model, random_string=random_string, utc_time=str(utc_time_seconds))
    message_in_request = Utility.decrypt_message_with_aes_key(encrypted_message=enc_message, aes_key=aes_key)
    logging.log(msg='message_in_request='+message_in_request, level=logging.ERROR)
    response_json = {
        "request_message":message_in_request
    }
    return jsonify(response_json)


if (__name__ == '__main__'):
    app.run()