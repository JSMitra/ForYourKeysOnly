from flask import Response, jsonify
import Constants
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Random import get_random_bytes
import logging
# for generating unique ids
import uuid 
# for md5 hashing
import hashlib
# UTC time
import time
# to convert binary to hex
import binascii

#for base64 encoding
import base64

# Importing libraries
import numpy as np
import random
import math
from collections import deque
import collections
import pickle
from datetime import datetime
import time

#for unzipping dataset
import os
import zipfile
import secrets

#Data processing
from numpy.linalg import norm

# for building ANN Model
import keras
from keras import layers
from keras import Sequential
from keras.layers import Input, Dense, Activation, Flatten, Dropout
from keras.initializers import RandomNormal, RandomUniform
import tensorflow as tf
from keras.optimizers import Adam, SGD

# for Tensorflow JS
import tensorflowjs as tfjs

# alternate combination of elements from two array
def interleave_two_arrays(arr1, arr2):
  return [element for pair in zip(arr1, arr2) for element in pair]

# given a string, produces its md5 hash
def get_binary_md5(input_string=''):
  md5_hash = hashlib.md5(input_string.encode('utf-8'))
  hex_string = md5_hash.hexdigest()
  #print(hex_string)
  #binary_md5 = "{0:08b}".format(int(hex_string, 16))
  binary_md5 = bin(int(hex_string, 16))[2:].zfill(128)
  return binary_md5

# takes utc time in seconds, converts it into a string and returns its md5 hash
def get_utc_md5(utc_time=0):
  utc_time_str = str(utc_time)
  return get_binary_md5(utc_time_str)

# given a string, produces its md5 hash in hex
def get_md5_hex_string(input_string=''):
  md5_hash = hashlib.md5(input_string.encode('utf-8'))
  hex_string = md5_hash.hexdigest()
  return hex_string

# given a binary string, converts it into a hex string by padding leading 0s if required
def convert_binary_string_to_hex_string(binary_string=''):
  binary_string_len = len(binary_string)
  leading_zeros_to_pad = binary_string_len % 4
  binary_string = ''.join(['0' for i in range(0, leading_zeros_to_pad)]) + binary_string
  binary_string_len = len(binary_string)
  # take 4 byte strings and convert them to hex character
  hex_string = ''
  hex_string_len = binary_string_len // 4
  for i in range(0,hex_string_len):
    hex_string = hex_string + hex(int(binary_string[i*4:i*4+4], 2))[2:]
  return hex_string

HEX_TO_BINARY = {'0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101', '6': '0110', '7': '0111', '8': '1000', '9': '1001', 'a': '1010', 'b': '1011', 'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111'}

# converts a hex string to a binary array using HEX_TO_BINARY map
def convert_hex_string_to_binary_array(hex_string=''):
  binary_string = ''
  for digit in [*hex_string]:
      binary_string += HEX_TO_BINARY[digit]
  binary_string_arr =  [*binary_string]
  binary_arr = [1 if i == '1' else 0 for i in binary_string_arr]
  return binary_arr

# takes two binary strings and joins them into a single numerical array with 0s and 1s by interleaving
def join_binary_strings_as_array(binary_string1='',binary_string2='', one=1, zero=0):
  combined_arr = interleave_two_arrays(binary_string1, binary_string2)
  total_len = len(combined_arr)
  arr = [zero for i in range(0,total_len)]
  for i in range(0,total_len):
    if combined_arr[i] == '1':
      arr[i] = one

  return arr

def do_quick_training(model, sample_size=256, training_epochs=10):
    inputs = []
    outputs = []
    for i in range(0, sample_size):
        random_string = str(uuid.uuid4())
        utc_time = int(time.time())
        input = np.array(join_binary_strings_as_array(get_binary_md5(random_string), get_utc_md5(utc_time)))
        inputs.append(input)
        y = np.array([random.random() for i in range(0,256)])
        outputs.append(y)
    inputs = np.array(inputs)
    outputs = np.array(outputs)
    model.fit(inputs, outputs, epochs=training_epochs, batch_size=sample_size, verbose=False)
    return model

# main function for generating simple or complex ANN
def generate_ANN(use_complex_model=False, learning_rate=0.05, 
                 quick_train=True, quick_train_sample_size=256, quick_train_training_epochs=10):
    
    model = Sequential()
    model.add(Dense(256, activation='tanh', input_dim=256, kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
    
    # build extra layers for a complex model
    if use_complex_model == True:
        model.add(Dense(256, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Flatten())
        model.add(Dense(512, activation='tanh'))
        model.add(Dense(512, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Dense(1024, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Flatten())
        model.add(Dense(1024, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Dense(2048, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Flatten())
        model.add(Dense(2048, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Flatten())
        model.add(Dense(1024, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Dense(1024, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Dense(2048, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Dense(512, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Dense(512, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
        model.add(Flatten())
        model.add(Dense(256, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
    
    model.add(Dense(256, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
    model.add(Dense(256, activation='tanh', kernel_initializer='RandomNormal', bias_initializer='he_uniform'))
    
    model.compile(loss='mse', optimizer=SGD(learning_rate=learning_rate), metrics=['accuracy', 'mse'])
    
    if quick_train:
        model = do_quick_training(model, sample_size=quick_train_sample_size, training_epochs=quick_train_training_epochs)
    
    return model

# a method that takes an ANN model, a random string and utc time in seconds to produce an ANN
# returns aes key hex string, aes key bits, ann raw output, input string fed into the ANN
def generate_aes_key(input_model, random_string='', utc_time='0'):
  input_bits = join_binary_strings_as_array(get_binary_md5(random_string), get_utc_md5(utc_time))
  input_bits_str = ['1' if i==1 else '0' for i in input_bits]
  input_str = convert_binary_string_to_hex_string(''.join(input_bits_str))
  input_arr = np.array(input_bits)
  input_arr = tf.expand_dims(input_arr, axis=0)

  # predict with random weights
  y = input_model.predict(input_arr, verbose=False)
  
  # pick the first value as we are giving only one input
  # raw_ann_output would be floating point values emerging from the ANN
  raw_ann_output = np.array(y[0])
  # compute the mean value of the floating point values obtained in raw_ann_output
  mean_value = np.mean(raw_ann_output)
  aes_key_256 = ['1' if i > mean_value else '0' for i in raw_ann_output]
  aes_key_256_str = ''.join(aes_key_256)
  aes_key_256_bits = [1 if i > mean_value else 0 for i in raw_ann_output]
  
  return convert_binary_string_to_hex_string(aes_key_256_str), aes_key_256_bits, raw_ann_output, input_str

SIMPLE_MODEL_JSON_TEMPLATE = 'simple_model_json_{suffix}.json'
SIMPLE_MODEL_H5_TEMPLATE = 'simple_model_h5_{suffix}.h5'
SIMPLE_TFJS_MODEL_TEMPLATE = 'simple_tfjs_model_{suffix}'

COMPLEX_MODEL_JSON_TEMPLATE = 'complex_model_json_{suffix}.json'
COMPLEX_MODEL_H5_TEMPLATE = 'complex_model_h5_{suffix}.h5'
COMPLEX_TFJS_MODEL_TEMPLATE = 'complex_tfjs_model_{suffix}'

# Model Saving function
def save_model(model, suffix='', is_complex=False,format='h5', drive_path='.', model_folder_path='/models/'):
    if len(suffix) == 0:
      suffix = str(time.time())
    if format == Constants.H5:
        if is_complex == True:
            model_file_name = drive_path + model_folder_path + COMPLEX_MODEL_H5_TEMPLATE.format(suffix=suffix)
        else:
            model_file_name = drive_path + model_folder_path + SIMPLE_MODEL_H5_TEMPLATE.format(suffix=suffix)
        model.save(model_file_name, overwrite=True)
        return model_file_name
    elif format == Constants.JSON:
        if is_complex == True:
            model_file_name = drive_path + model_folder_path + COMPLEX_MODEL_JSON_TEMPLATE.format(suffix=suffix)
        else:
            model_file_name = drive_path + model_folder_path + SIMPLE_MODEL_JSON_TEMPLATE.format(suffix=suffix)
        model_json = model.to_json()
        model_json_file = open(model_file_name, "w")
        model_json_file.write(model_json)
        return model_file_name
    elif format == Constants.TFJS:
        if is_complex == True:
          model_folder_name = model_folder_path + COMPLEX_TFJS_MODEL_TEMPLATE.format(suffix=suffix)
          model_folder_full_path = drive_path + model_folder_name
        else:
          model_folder_name = model_folder_path + SIMPLE_TFJS_MODEL_TEMPLATE.format(suffix=suffix)
        
        model_folder_full_path = drive_path + model_folder_name
        tfjs.converters.save_keras_model(model,model_folder_full_path)
        return model_folder_name
    return None

BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-s.index(s[len(s) - 1:])]

def pad_bytes(plain_text_bytes, block_size=BLOCK_SIZE,pad_with_chr=chr(0)):
  bytes_to_pad = block_size - len(plain_text_bytes) % block_size
  padding_bytes = (bytes_to_pad*pad_with_chr).encode('utf-8')
  padded_bytes = plain_text_bytes + padding_bytes
  return padded_bytes

def unpad_bytes(decrypted_bytes_padded):
  last_char_padded = decrypted_bytes_padded[len(decrypted_bytes_padded) - 1:]
  last_char_padded_first_occurance = decrypted_bytes_padded.index(last_char_padded)
  return decrypted_bytes_padded[:last_char_padded_first_occurance]

# function thats takes the model file/folder path, RSA public key
# and ecrypts it
def encrypt_model(model_file_path, rsa_public_key, format=Constants.H5):
    if format == Constants.H5:
        aes_key = get_random_bytes(16)
        rsa_cipher = PKCS1_OAEP.new(rsa_public_key)
        aes_key_encrypted = rsa_cipher.encrypt(aes_key)
        aes_key_encrypted_base64 = base64.b64encode(aes_key_encrypted).decode("ascii")
        aes_cipher = AES.new(aes_key, AES.MODE_ECB)
        model_file = open(model_file_path, "rb")
        contents = model_file.read()
        #base64 encode the contents
        contents_b64 = base64.b64encode(contents)
        contents_b64 = pad_bytes(contents_b64)
        contents_encrypted = aes_cipher.encrypt(contents_b64)
        model_file_encrypted = open(model_file_path + '.encrypted', 'wb')
        model_file_encrypted.write(contents_encrypted)
        model_file_encrypted_path = model_file_encrypted.name
        model_file.close()
        model_file_encrypted.close()
        return model_file_encrypted_path, aes_key_encrypted_base64
    
def compose_get_ann_response(model_file_path, ann_id="ann_id",format=Constants.H5, is_encrypted=True, aes_key_encrypted_base64=Constants.NA):
  ann_response_json = {}
  if format == Constants.H5:
    ann_file = open(model_file_path, "rb")
    ann_file_contents = ann_file.read()
    ann_file_contents_b64_encoded = base64.b64encode(ann_file_contents).decode("ascii")
    ann_response_json = {
        Constants.FORMAT: Constants.H5,
        Constants.IS_ENCRYPTED: is_encrypted,
        Constants.ANN_ID: ann_id,
        Constants.ANN_BASE64: ann_file_contents_b64_encoded,
        Constants.AES_KEY_ENCRYPTED: aes_key_encrypted_base64
    }
  #return Response(jsonify(get_ann_response_json), mimetype='application/json')
  elif format == Constants.TFJS:
    ann_response_json = {
      Constants.FORMAT: Constants.TFJS,
      Constants.IS_ENCRYPTED: False,
      Constants.ANN_ID: model_file_path
      }
  return jsonify(ann_response_json)

def get_error_json(err_msg='Error!'):
  error_json = {
     "error_message": err_msg
     }
  return jsonify(error_json)

def is_content_type_not_json(request):
  content_type = request.headers.get('Content-Type')
  if content_type != Constants.APPLICATION_JSON:
    err_msg = f'content type {content_type} not supported.'
    error_json = {
       "error_message": err_msg
       }
    return jsonify(error_json)
  
  # content type is json
  return None

def decrypt_message_with_aes_key(encrypted_message, aes_key):
  # use the AES key to decrypt the secret message
  try:
    enc_message_bytes = base64.b64decode(encrypted_message)
    aes_key_bytes = bytes.fromhex(aes_key)
    cipher = AES.new(key=aes_key_bytes,mode=AES.MODE_ECB)
    decrypted_bytes_padded = cipher.decrypt(enc_message_bytes)
    decrypted_bytes = unpad_bytes(decrypted_bytes_padded)
    message = base64.b64decode(decrypted_bytes).decode("utf-8")
  except:
     logging.log(msg="Error while decrypting", level=logging.ERROR)
     return "could not decrypt", False
  return message, True
   