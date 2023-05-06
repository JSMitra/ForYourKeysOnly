package edu.fyko.java;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URISyntaxException;
import java.security.InvalidKeyException;
import java.security.Key;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import java.security.NoSuchProviderException;
import java.security.Security;
import java.util.HexFormat;
import java.util.UUID;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.spec.SecretKeySpec;

import org.bouncycastle.util.encoders.Base64;
import org.deeplearning4j.nn.modelimport.keras.KerasModelImport;
import org.deeplearning4j.nn.modelimport.keras.exceptions.InvalidKerasConfigurationException;
import org.deeplearning4j.nn.modelimport.keras.exceptions.UnsupportedKerasConfigurationException;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.json.JSONObject;

public class FYKO {

	private static final String SERVER_GET_ANN_ENDPOINT = "http://localhost:8000/get_ann";
	private static final String SERVER_SEND_MESSAGE = "http://localhost:8000/send_message";

	public static void main(String[] args)
			throws NoSuchAlgorithmException, URISyntaxException, IOException, InterruptedException,
			NoSuchPaddingException, InvalidKeyException, IllegalBlockSizeException, BadPaddingException,
			NoSuchProviderException, InvalidKerasConfigurationException, UnsupportedKerasConfigurationException {

		Security.addProvider(new org.bouncycastle.jce.provider.BouncyCastleProvider());

		System.out.println("FYKO Java Client.");
		// Step 1: Generate RSA Key pair
		System.out.println("\nStep 1: Generate RSA Keypair");
		KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA");
		keyPairGenerator.initialize(2048);
		KeyPair keyPair = keyPairGenerator.generateKeyPair();
		Key pub_key = keyPair.getPublic();
		Key pvt_key = keyPair.getPrivate();
		String pub_key_pem = Utility.getBase64String(pub_key.getEncoded());

		System.out.println("\nStep 2: Build payload to get ann from server.");
		JSONObject jsonObject = new JSONObject();
		jsonObject.put("format", "h5");
		jsonObject.put("rsa_public_key_2048_base64", pub_key_pem);
		System.out.println("Payload for getting ann:" + jsonObject.toString());

		System.out.println("\nStep 3: Send payload to server.");
		String responseJson = Utility.sendPayLoad(SERVER_GET_ANN_ENDPOINT, jsonObject.toString());

		System.out.println("\nStep 4: Parse the payload obtained from the server containing the encrypted ann model");
		JSONObject annResponseObject = new JSONObject(responseJson);
		String annId = annResponseObject.getString("ann_id");
		System.out.println("annId=" + annId);
		String ann_base64 = annResponseObject.getString("ann_base64");
		byte[] annH5BytesEncrypted = Utility.decodeBase64(ann_base64);
		String encryptedAesKeyBase64 = annResponseObject.getString("aes_key_encrypted");
		byte[] encryptedAesKeyBytes = Utility.decodeBase64(encryptedAesKeyBase64);
		Cipher rsaCipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA1AndMGF1Padding", "BC");// PKCS1-OAEP
		rsaCipher.init(Cipher.DECRYPT_MODE, pvt_key);
		System.out.println("\nStep 5: Decryting AES Key used to encrypt the model.");
		byte[] aesKeyBytes = rsaCipher.doFinal(encryptedAesKeyBytes);
		SecretKeySpec key = new SecretKeySpec(aesKeyBytes, "AES");

		System.out.println("\nStep 6: Decryting ANN Model using the AES Key");
		Cipher aesCipher = Cipher.getInstance("AES/ECB/ZeroBytePadding", "BC");
		aesCipher.init(Cipher.DECRYPT_MODE, key);
		byte[] annH5BytesBase64 = aesCipher.doFinal(annH5BytesEncrypted);
		byte[] annH5Bytes = Base64.decode(annH5BytesBase64);

		System.out.println("\nStep 7: Save the model to file:" + annId);
		Utility.writeToFile("./" + annId, annH5Bytes);

		System.out.println("\nStep 8: Load the model with name:" + annId);
		InputStream h5FileStream = new FileInputStream("./" + annId);
		MultiLayerNetwork model = KerasModelImport.importKerasSequentialModelAndWeights(h5FileStream, false);
		
		System.out.println("\nStep 9: Build message payload to send to the server");
		long utcTimeSeconds = System.currentTimeMillis()/1000;
		String randomString = UUID.randomUUID().toString();
		String aesKey = Utility.generateAESKey(model, utcTimeSeconds, randomString);
		aesKeyBytes = HexFormat.of().parseHex(aesKey);
		System.out.println("UTC Time="+utcTimeSeconds+", randomString="+randomString+",aesKey="+aesKey);
		JSONObject sendMessage = new JSONObject();
		String secretMessage = "message id:"+UUID.randomUUID().toString()+" \nHi in Telugu:హాయ్, \nHi in Chinese:你好, \nHi in Japanese:やあ";
		System.out.println("Secret Message:"+secretMessage);
		String secretMessageBase64 = Utility.getBase64String(secretMessage.getBytes());
		aesCipher = Cipher.getInstance("AES/ECB/ZeroBytePadding", "BC");
		key = new SecretKeySpec(aesKeyBytes, "AES");
		aesCipher.init(Cipher.ENCRYPT_MODE, key);
		byte[] secretMessageEncryptedBytes = aesCipher.doFinal(secretMessageBase64.getBytes());
		String secretMessageEncryptedBytesBase64 = Utility.getBase64String(secretMessageEncryptedBytes);
		sendMessage.put("random_string", randomString);
		sendMessage.put("utc_time_seconds", utcTimeSeconds);
		sendMessage.put("encrypted_message", secretMessageEncryptedBytesBase64);
		sendMessage.put("ann_id", annId);
		String sendMessageString = sendMessage.toString();
		System.out.println("Sending secret message to server:"+sendMessageString);
		responseJson = Utility.sendPayLoad(SERVER_SEND_MESSAGE, sendMessageString);
		System.out.println("Response from Server:"+responseJson);
		JSONObject receivedResponseObj = new JSONObject(responseJson);
		String receivedMessage = receivedResponseObj.getString("request_message");
		
		System.out.println("\nStep 10: Verify if the Server was able to decrypt the message.");
		System.out.println("Original Message:"+secretMessage);
		System.out.println("Message decoded by Server:"+receivedMessage);
		System.out.println("Is the original secret message sent equal to the request message in response:"+secretMessage.equals(receivedMessage));
		
		System.out.println("\nStep 11: sending a stale request which is older than 10 seconds to the server");
		utcTimeSeconds = System.currentTimeMillis()/1000 - 20;
		sendMessage.put("random_string", randomString);
		sendMessage.put("utc_time_seconds", utcTimeSeconds);
		sendMessage.put("encrypted_message", secretMessageEncryptedBytesBase64);
		sendMessage.put("ann_id", annId);
		sendMessageString = sendMessage.toString();
		responseJson = Utility.sendPayLoad(SERVER_SEND_MESSAGE, sendMessageString);
		System.out.println("Response from Server:"+responseJson);
		
		System.out.println("\nStep 12: sending a future request which is older than 10 seconds to the server");
		utcTimeSeconds = System.currentTimeMillis()/1000 + 20;
		sendMessage.put("random_string", randomString);
		sendMessage.put("utc_time_seconds", utcTimeSeconds);
		sendMessage.put("encrypted_message", secretMessageEncryptedBytesBase64);
		sendMessage.put("ann_id", annId);
		sendMessageString = sendMessage.toString();
		responseJson = Utility.sendPayLoad(SERVER_SEND_MESSAGE, sendMessageString);
		System.out.println("Response from Server:"+responseJson);
		
		
	}
}
