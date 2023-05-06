# ForYourKeysOnly (FYKO)
Cyber Security Application using AES Key Generation through ANNs

## ForYourKeysOnly or FYKO is a Project that makes use of ANNs for Generation of AES Keys which inturn can be used to encrypt data.
ANNs bring the advantages of generating chaotic outputs which are sensitive to vatying inputs. Exploiting this behavior, AES Keys are generated 
using deterministic inputs to the ANN. A Client and a Server can share a common ANN Model for secure communication. 
The Client can make a request to securely obtain an ANN Model from the Server which has a unique ID (ANN ID). 
The Client can then feed deterministic inputs into the ANN Model to obtain random AES Keys and  can encrypt request data using that AES Key. 
The Client just has to share the deterministic inputs, ANN ID and the encrypted data with the Server. 
The Server, using the ANN ID can fetch the ANN Model from storage, re-play the deterministic inputs on the ANN to obtain the same AES Key that the Client 
had produced at its end and decrypt Client's request data.

In the whole design, sharing of AES Keys over the network is prevented. The only important requirement would be to trasmit the ANN Model itself securely
from the Server to the Client. Using standard native Clients based on Java or Python Runtime, it is easy to produce RSA Keypairs at the Client side and 
share the RSA Public Key with the Server to encrypt the ANN Model. For Javascript based Clients running on browser, this approach may not work and 
secure delivery of ANN Model solely depends SSL/TLS communication using HTTPS.

This project depicts the Proof of Concept(POC) of usability of ANNs for the desired job of AES Key production. It also depicts three different Clients 
(Python, Java and Javascript) to show how they can interact with a Python based Flask Application Server which can serve ANN Models securely and also take
encrypted requests from the client and decrypt them.

Following are the important Sub-Projects:

	- FYKO_JupyterNotebook folder consists of the Jupyter notebook which showcases the entire POC (Model Generation, Experiments) followed by a Python Client
	  Code to interact with the Flask Application server.
   
	- FYKO_FlaskApplication folder consists of code to run a Flask Application to serve ANN Models and to receive encrypted requests from FYKO Clients. this
      folder also consists of FYKO_JS Client which has FYKO.js script which loads into the browser and fetches Tensorflowjs based Model for secure communication.
   
	- FYKO_Clients folder consists of a FYKO_Java project which illustrates secure communication with Flask Application using Java code

Each folder would be provided with its README.md file consisting of Setup and other instructions.

