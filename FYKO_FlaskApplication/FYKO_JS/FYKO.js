function interleave_binary_strings(binarystring1, binarystring2){
    var resultstring = ''
    if(binarystring1.length == binarystring2.length){
        var binarystring1_len = binarystring1.length;
        for(var i=0;i<binarystring1_len;i++){
            resultstring += ''+binarystring1.charAt(i)+binarystring2.charAt(i);
        }
    }
    return resultstring;
}

function getHexString(binaryString){
    var hexstring = ''
    if(binaryString && binaryString.length%4==0){
        for(var i=0;i<binaryString.length;i+=4){
            var fourBits = binaryString.substring(i,i+4);
            var hexBit = parseInt(fourBits, 2).toString(16); 
            hexstring += hexBit
        }
    }

    return hexstring
}

function getBinaryString(hexstring){
    var binarystring = ''
    if(hexstring){
        var hexstring_len = hexstring.length;
        for(var i=0; i< hexstring.length;i++){
           var c = hexstring.charAt(i)
            switch(c){
                case '0': binarystring += '0000';break;
                case '1': binarystring += '0001';break;
                case '2': binarystring += '0010';break;
                case '3': binarystring += '0011';break;
                case '4': binarystring += '0100';break;
                case '5': binarystring += '0101';break;
                case '6': binarystring += '0110';break;
                case '7': binarystring += '0111';break;
                case '8': binarystring += '1000';break;
                case '9': binarystring += '1001';break;
                case 'a': binarystring += '1010';break;
                case 'b': binarystring += '1011';break;
                case 'c': binarystring += '1100';break;
                case 'd': binarystring += '1101';break;
                case 'e': binarystring += '1110';break;
                case 'f': binarystring += '1111';break;
            }
        }
    }
    return binarystring
}

function getBinaryArrayFromBinaryString(binaryString){
    var binary_array = []
    if(binaryString){
        for(var i=0;i<binaryString.length;i++){
            var c = binaryString.charAt(i)
            if (c == '0'){
                binary_array[i]=0
            }else{
                binary_array[i]=1
            }
        }
    }
    return binary_array
}

function getAesKeyBinaryString(floatArray, mean_value){
    var binaryString = ''
    if(floatArray && floatArray.length >0){
        for(var i=0;i<floatArray.length;i++){
            var value = floatArray[i]
            if(value > mean_value){
                binaryString += '1'
            }else{
                binaryString += '0'
            }
        }
    }
    return binaryString
}

var fyko_output = "fyko_output"


if(window.localStorage)
{
    document.getElementById(fyko_output).innerHTML += "<br/><br/> Local storage supported. ANN model will be stored in localstorage";
}
document.getElementById(fyko_output).innerHTML += "<br/><br/> Illustrating ANN model fetch in tfjs format followed by secure message exchange...";

// Step1: Prepare payload to fetch a simple ANN from server
var request_get_ann = JSON.stringify({"format":"tfjs"})
document.getElementById(fyko_output).innerHTML += "<br/><br/> Step1: Prepare a payload to request a Simple ANN Model from Server. Payload = "+request_get_ann;

// Step2: request for a TFJS based Simple ANN
document.getElementById(fyko_output).innerHTML += "<br/><br/> Step2: Fetch a Simple ANN Model in TFJS Format";
let response = await new Promise(resolve => {
    var xhr_get_ann = new XMLHttpRequest(); 
    xhr_get_ann.open("POST", '/get_ann'); 
    xhr_get_ann.setRequestHeader("Content-Type", "application/json");
    xhr_get_ann.onload = function(e) {
        resolve(xhr_get_ann.response);
      };
      xhr_get_ann.onerror = function () {
        resolve(undefined);
        console.error("Error case");
      };
    xhr_get_ann.send(request_get_ann);
 })

var json_response = JSON.parse(response);
document.getElementById(fyko_output).innerHTML += "<br/><br/> Response from Server = "+response;

var ann_id = json_response['ann_id']
document.getElementById(fyko_output).innerHTML += "<br/><br/> ANN ID obtained from Server = "+ann_id;

// Step 3: Form the url to load the model.json file using the ann_id
var model_json_url = 'http://localhost:8000/tfjs/'+ann_id+'/model.json'
document.getElementById(fyko_output).innerHTML += "<br/><br/> Step 3: Form the url to load model.json. URL = "+model_json_url;


document.getElementById(fyko_output).innerHTML += "<br/><br/> Step 4: Load the tfjs model using tf library";
const model = await tf.loadLayersModel(model_json_url);
document.getElementById(fyko_output).innerHTML += "<br/> Model "+ann_id+" loaded into localstorage.";

document.getElementById(fyko_output).innerHTML += "<br/><br/> Step 5: Use the ANN model to generate AES Key";
const d = new Date();
var current_time = Math.round(d.getTime()/1000);
document.getElementById(fyko_output).innerHTML += "<br/> Current UTC Time in Seconds = "+current_time;
var random_string = window.crypto.randomUUID()
document.getElementById(fyko_output).innerHTML += "<br/> Random String = "+random_string;
var current_time_hash = CryptoJS.MD5(''+current_time).toString();
var random_string_hash = CryptoJS.MD5(random_string).toString();
document.getElementById(fyko_output).innerHTML += "<br/> Get MD5 Hashes of current UTC seconds and random string. Combine their binary bits and feed into ANN.";
var binary_input_string = interleave_binary_strings(getBinaryString(random_string_hash), getBinaryString(current_time_hash))
var combined_hex_string = getHexString(binary_input_string)
var binary_input = getBinaryArrayFromBinaryString(binary_input_string)
// Generate AES Key
var prediction = model.predict(tf.expandDims(binary_input,0));
var predictionArray = prediction.dataSync()
var mean_value = tf.mean(predictionArray).dataSync()[0]
var aesKeyBinaryString = getAesKeyBinaryString(predictionArray, mean_value)
var aesKeyHexString = getHexString(aesKeyBinaryString)
document.getElementById(fyko_output).innerHTML += "<br/><br/>AES Key Generated = "+aesKeyHexString;

// Step 6: Prepare a secret message to be sent to the server using AES Key generated.
document.getElementById(fyko_output).innerHTML += "<br/><br/> Step 6: Prepare a secret message to be sent to the server using AES Key generated.";
var multilingual_string = "English: FYKO is a cool project \nTelugu: FYKO ఒక మంచి ప్రాజెక్ట్ \nHindi: FYKO एक अच्छा प्रोजेक्ट है \nPortugese: FYKO é um projeto legal \nThai: FYKO เป็นโครงการที่ยอดเยี่ยม \nChinese: FYKO是一個很酷的項目 \nJapanese: FYKOはクールなプロジェクトです \nKorean: FYKO는 멋진 프로젝트입니다 \nIrish: Is tionscadal fionnuar é FYKO \nArabic: FYKO مشروع رائع" 
var secret_message = "message id:" + window.crypto.randomUUID() + "\n" + multilingual_string
document.getElementById(fyko_output).innerHTML += "<br/><br/> secret_message = "+secret_message;
var secret_message_uri_encoded = encodeURIComponent(secret_message)
document.getElementById(fyko_output).innerHTML += "<br/><br/> secret_message_uri_encoded = "+secret_message_uri_encoded;
var secret_message_b64_string = window.btoa(secret_message_uri_encoded)
document.getElementById(fyko_output).innerHTML += "<br/><br/> secret_message_b64_string = "+secret_message_b64_string;
var key = CryptoJS.enc.Hex.parse(aesKeyHexString);
var encrypted_message = CryptoJS.AES.encrypt(secret_message_b64_string, key, { mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.ZeroPadding });
document.getElementById(fyko_output).innerHTML += "<br/><br/> encrypted_message = "+encrypted_message;

// Step 7: Send encrypted message to server
document.getElementById(fyko_output).innerHTML += "<br/><br/> Step 7: Send encrypted message to server";
var send_message_obj = new Object();
send_message_obj.format="tfjs"
send_message_obj.is_message_uri_encoded=true
send_message_obj.random_string = random_string
send_message_obj.utc_time_seconds = current_time
send_message_obj.random_string = random_string
send_message_obj.encrypted_message = encrypted_message.toString();
send_message_obj.ann_id = ann_id
var send_message_string = JSON.stringify(send_message_obj)

document.getElementById(fyko_output).innerHTML += "<br/><br/> Sending message = "+send_message_string;
response = await new Promise(resolve => {
    var xhr_send_message = new XMLHttpRequest(); 
    xhr_send_message.open("POST", '/send_message'); 
    xhr_send_message.setRequestHeader("Content-Type", "application/json");
    xhr_send_message.onload = function(e) {
        resolve(xhr_send_message.response);
      };
      xhr_send_message.onerror = function () {
        resolve(undefined);
        console.error("Error case");
      };
      xhr_send_message.send(send_message_string);
 })

 // Step 8: Verify if Server is able to decrypt the message correctly
 json_response = JSON.parse(response);
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Step 8: Verify if Server is able to decrypt the message correctly";
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Response from server after decoding = "+response;
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Original Message: = "+secret_message;
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Message decoded by Server: = "+json_response['request_message'];
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Is the original secret message sent equal to the request message in response: = "+(json_response['request_message'] == secret_message);


// send another sample encrypted message
current_time = Math.round(d.getTime()/1000);
random_string = window.crypto.randomUUID()
current_time_hash = CryptoJS.MD5(''+current_time).toString();
random_string_hash = CryptoJS.MD5(random_string).toString();
binary_input_string = interleave_binary_strings(getBinaryString(random_string_hash), getBinaryString(current_time_hash))
combined_hex_string = getHexString(binary_input_string)
binary_input = getBinaryArrayFromBinaryString(binary_input_string)
prediction = model.predict(tf.expandDims(binary_input,0));
predictionArray = prediction.dataSync()
mean_value = tf.mean(predictionArray).dataSync()[0]
aesKeyBinaryString = getAesKeyBinaryString(predictionArray, mean_value)
aesKeyHexString = getHexString(aesKeyBinaryString)
secret_message = "message id:" + window.crypto.randomUUID() + "; Simple message!"
document.getElementById(fyko_output).innerHTML += "<br/><br/>Step 9: Sending another message = "+secret_message;
secret_message_uri_encoded = encodeURIComponent(secret_message)
secret_message_b64_string = window.btoa(secret_message_uri_encoded)
key = CryptoJS.enc.Hex.parse(aesKeyHexString);
encrypted_message = CryptoJS.AES.encrypt(secret_message_b64_string, key, { mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.ZeroPadding });
send_message_obj = new Object();
send_message_obj.format="tfjs"
send_message_obj.is_message_uri_encoded=true
send_message_obj.random_string = random_string
send_message_obj.utc_time_seconds = current_time
send_message_obj.random_string = random_string
send_message_obj.encrypted_message = encrypted_message.toString();
send_message_obj.ann_id = ann_id
var send_message_string = JSON.stringify(send_message_obj)
document.getElementById(fyko_output).innerHTML += "<br/><br/> Sending message = "+send_message_string;
response = await new Promise(resolve => {
    var xhr_send_message = new XMLHttpRequest(); 
    xhr_send_message.open("POST", '/send_message'); 
    xhr_send_message.setRequestHeader("Content-Type", "application/json");
    xhr_send_message.onload = function(e) {
        resolve(xhr_send_message.response);
      };
      xhr_send_message.onerror = function () {
        resolve(undefined);
        console.error("Error case");
      };
      xhr_send_message.send(send_message_string);
 })
 json_response = JSON.parse(response);
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Verify if Server is able to decrypt the simple message correctly";
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Response from server after decoding = "+response;
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Original Message: = "+secret_message;
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Message decoded by Server: = "+json_response['request_message'];
 document.getElementById(fyko_output).innerHTML += "<br/><br/> Is the original secret message sent equal to the request message in response: = "+(json_response['request_message'] == secret_message);

 // Step 10:
current_time = Math.round(d.getTime()/1000);
current_time = current_time - 20
document.getElementById(fyko_output).innerHTML += "<br/><br/> Step 10: Replay Attack Scenario";
send_message_obj.utc_time_seconds = current_time
send_message_string = JSON.stringify(send_message_obj)
response = await new Promise(resolve => {
    var xhr_send_message = new XMLHttpRequest(); 
    xhr_send_message.open("POST", '/send_message'); 
    xhr_send_message.setRequestHeader("Content-Type", "application/json");
    xhr_send_message.onload = function(e) {
        resolve(xhr_send_message.response);
      };
      xhr_send_message.onerror = function () {
        resolve(undefined);
        console.error("Error case");
      };
      xhr_send_message.send(send_message_string);
 })
 json_response = JSON.parse(response);
 document.getElementById(fyko_output).innerHTML += "<br/> Response from server ="+response;

// Step 10:
current_time = Math.round(d.getTime()/1000);
current_time = current_time + 20
document.getElementById(fyko_output).innerHTML += "<br/><br/> Step 11: Send future message";
send_message_obj.utc_time_seconds = current_time
send_message_string = JSON.stringify(send_message_obj)
response = await new Promise(resolve => {
    var xhr_send_message = new XMLHttpRequest(); 
    xhr_send_message.open("POST", '/send_message'); 
    xhr_send_message.setRequestHeader("Content-Type", "application/json");
    xhr_send_message.onload = function(e) {
        resolve(xhr_send_message.response);
      };
      xhr_send_message.onerror = function () {
        resolve(undefined);
        console.error("Error case");
      };
      xhr_send_message.send(send_message_string);
 })
 json_response = JSON.parse(response);
 document.getElementById(fyko_output).innerHTML += "<br/> Response from server ="+response;
