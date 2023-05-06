# FYKO Flask Application
An application server which can Serve ANN Models and interact with client securely using those Models.

    Setup:
        - Open this project in Visual Studio Code
        - Open Terminal
        - Create a python virtual environment using command: python -m  venv <environment name>
        - Active the environment using .\<environment name>\Scripts\activate command (set powershell script execution policy to run the activate ps command)
        - Upgrade to latest PIP using command:python.exe -m pip install --upgrade pip
        - Then to install required packages, the run the following commands
            - pip install tensorflow
            - pip install tensorflowjs
            - pip install pycryptodome
            - pip install flask
            - pip install python-dotenv
            - pip install protobuf==3.20.* (if protobuf >= 3.19.0 needed)
        - Tensorflowjs requires jszip javacript library. Download from https://stuk.github.io/jszip/ the latest zip file and place it in this folder. Update the distribution path (dist path) in Constants.py JSZIP_DIRECTORY variable. Update JSZIP_JS_FILE variable to point to jszip.min.js file (or the file recommended by JSZIP website)

    Project Information:
        -This project runs a Python FYKO Flask Server which serves ANN models
        - /get_ann endpoint takes in Client given RSA Public and serves a json response containing ecrypted model.
            - For simplicity, simple ANN model H5 format is used as it requires around 1MB of storage space. Sending 1MB json data seems to work fine. For Complex ANN, different strategy needs to be applied to serve the encrypted file in chunks (either encrypt entire file and send it in chunks or send encrypted chunks which can be assembled by the client)
            - For Tensorflow JS (TFJS) based clients, TFJS format is used which makes a model directory containing the model.json file along with shards of .bin files representing the weights of the ANN. For a Simple ANN, the number of shards is one. For Complex ANN, around 15 shards of .bin files each 4K bytes is created. Since Tensorflow JS current does not support encryption, this Flask application serves TFJS model directory as files as TFJS Client library seeks model.json URL and replaced model.json with individual .bin shard requests
            - TFJS Clients could use HTTPS scheme run on a trusted server to get the TFJS ANN Model files due to restricted model loading options in TFJS
        - This application produes all the ANN models in ./models directory
        - This application does not optimise model generartion, fetching or caching as it just illustrates FYKO concepts of sharing ecnrypted ANN models to clients.
        - This application does not work with any authentication as Authentication/Authorization can be implemented in production using standard login mechanisms.

    Running the FYKO application:
        - Open FYKO.py and run the application in debug on run mode
        - This application URL is used in FYKO.ipynb Jupyter notebook as a part of Experiment to check Python Client interacting with this server
