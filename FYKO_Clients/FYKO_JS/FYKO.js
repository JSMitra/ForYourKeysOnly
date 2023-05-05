if(window.localStorage)
{
    console.log("local storage supported !");
}

function saveTfjsZip(pdf, key) {
    console.log("In saveTfjsZip")
    var fileReader = new FileReader();

    fileReader.onload = function (evt) {
        var result = evt.target.result;

        try {
            console.log('result='+result)
            var prefix = 'data:application/x-zip-compressed;base64,';
            console.log('Prefix len='+prefix.length)
            var base64ZipString = result.substring(prefix.length)
            console.log('base64ZipString:'+base64ZipString)
            localStorage.setItem(key, result);
            var new_zip = new JSZip();
            new_zip.loadAsync(base64ZipString,{base64: true}).then(async function(zip){
                //var jsonFile = await zipped.file("model.json").async("text");
                Object.keys(zip.files).forEach(function (filename) {
                    zip.files[filename].async('string').then(function (fileData) {
                      console.log('filename:'+filename+',fileData:'+fileData) // These are your file contents
                      localStorage.setItem(filename, fileData);      
                    })
                  })
            });
        } catch (e) {
            console.log("Storage failed: " + e);
        }
    };

    fileReader.readAsDataURL(pdf);
}

// model zip download
var xhr = new XMLHttpRequest(); 
xhr.open("GET", "/data/tfjs.zip"); 
xhr.responseType = "blob";
xhr.onload = function() {
    console.log("XMLHttpRequest, xhr.status="+xhr.status)
    if(xhr.status && xhr.status === 200) {
        saveTfjsZip(xhr.response, "tfjs.zip");
    } 
}
xhr.send();

const model = await tf.loadLayersModel('http://localhost:8000/data/tfjs/model.json');
console.log("model loaded !");
const saveResults = model.save('localstorage://my-model-1');

const model2 = await tf.loadLayersModel('localStorage://tfjs/model.json');
console.log("model2 loaded !");

if(window.crypto.subtle)
{
    console.log("subtle crypto there !");
}
// declare all characters

const characters ='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';

function generateString(length) {
    let result = ' ';
    const charactersLength = characters.length;
    for ( let i = 0; i < length; i++ ) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
    }

    return result;
}

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
    console.log(hexstring)
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

const d = new Date();
//var current_time = Math.round(d.getTime()/1000);
var current_time = 1682784885;
//var random_string = window.crypto.randomUUID()
var random_string = '6kn^,HU';
var current_time_hash = CryptoJS.MD5(''+current_time).toString();
console.log("md5 of current_time "+current_time+":"+current_time_hash);
var random_string_hash = CryptoJS.MD5(random_string).toString();
console.log("md5 of random_string "+random_string+":"+random_string_hash);
var binary_input_string = interleave_binary_strings(getBinaryString(random_string_hash), getBinaryString(current_time_hash))
console.log('Combined input string:'+binary_input_string)
var combined_hex_string = getHexString(binary_input_string)
console.log('Combined input hex:'+combined_hex_string)
var binary_input = getBinaryArrayFromBinaryString(binary_input_string)
console.log('Combined binary_input:'+binary_input)

// prediction
const prediction = model.predict(tf.expandDims(binary_input,0));
var predictionArray = prediction.dataSync()
var mean_value = tf.mean(predictionArray).dataSync()[0]
var aesKeyBinaryString = getAesKeyBinaryString(predictionArray, mean_value)
console.log('aesKeyBinaryString:'+aesKeyBinaryString)
var aesKeyHexString = getHexString(aesKeyBinaryString)
console.log('aesKeyHexString:'+aesKeyHexString)
prediction.print();