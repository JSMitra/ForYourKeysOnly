package edu.fyko.java;

import java.io.File;
import java.io.IOException;
import java.math.BigInteger;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpResponse.BodyHandlers;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.FileUtils;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.factory.Nd4j;

public class Utility {

	public static String getBase64String(byte[] bytes) {
		return Base64.encodeBase64String(bytes);
	}

	public static byte[] decodeBase64(String base64String) {
		return Base64.decodeBase64(base64String);
	}

	public static String getMd5(String input) {
		try {
			// Static getInstance method is called with hashing MD5
			MessageDigest md = MessageDigest.getInstance("MD5");

			// digest() method is called to calculate message digest
			// of an input digest() return array of byte
			byte[] messageDigest = md.digest(input.getBytes());

			// Convert byte array into signum representation
			BigInteger no = new BigInteger(1, messageDigest);

			// Convert message digest into hex value
			String hashtext = no.toString(16);
			while (hashtext.length() < 32) {
				hashtext = "0" + hashtext;
			}
			return hashtext;
		}

		// For specifying wrong message digest algorithms
		catch (NoSuchAlgorithmException e) {
			throw new RuntimeException(e);
		}
	}

	public static int[] getBinaryArrayFromHexString(String hexString) {
		int length = hexString.length();
		int[] result = new int[length * 4];
		int currentPointer = 0;
		for (int i = 0; i < length; i++) {
			int hexValue = Integer.parseInt("" + hexString.charAt(i), 16);
			String binaryString = Integer.toBinaryString(hexValue);
			int zeroToPrefix = 4 - binaryString.length();
			for (int j = 0; j < zeroToPrefix; j++) {
				result[currentPointer++] = 0;
			}
			for (int j = 0; j < binaryString.length(); j++) {
				result[currentPointer++] = binaryString.charAt(j) - '0';
			}
		}

		return result;
	}

	public static String getHexStringFromBinaryArray(int[] binaryArray) {
		int length = binaryArray.length;
		StringBuffer sb = new StringBuffer();
		for (int i = 0; i < length; i += 4) {
			StringBuffer binaryString = new StringBuffer();
			binaryString.append(binaryArray[i]);
			binaryString.append(binaryArray[i + 1]);
			binaryString.append(binaryArray[i + 2]);
			binaryString.append(binaryArray[i + 3]);
			int decimal = Integer.parseInt(binaryString.toString(), 2);
			String hexStr = Integer.toString(decimal, 16);
			sb.append(hexStr);
		}

		return sb.toString();
	}

	public static int[] interleaveArrays(int[] a1, int[] a2) {
		int len = a1.length;
		int result[] = new int[len * 2];
		int pos = 0;
		for (int i = 0; i < len; i++) {
			result[pos++] = a1[i];
			result[pos++] = a2[i];
		}
		return result;
	}

	public static String sendPayLoad(String uri, String payload)
			throws URISyntaxException, IOException, InterruptedException {
		HttpRequest request = HttpRequest.newBuilder().setHeader("Content-Type", "application/json").uri(new URI(uri))
				.POST(HttpRequest.BodyPublishers.ofString(payload)).build();
		HttpClient client = HttpClient.newHttpClient();
		HttpResponse<String> response = client.send(request, BodyHandlers.ofString());
		String responseJsonString = response.body();
		return responseJsonString;
	}

	public static void writeToFile(String filePath, byte[] bytes) throws IOException {
		FileUtils.writeByteArrayToFile(new File(filePath), bytes);
	}

	public static String generateAESKey(MultiLayerNetwork model, long utcTimeSeconds, String randomString) {
		String utcStr = ""+ utcTimeSeconds;
		int[] randomStringMD5Array = Utility.getBinaryArrayFromHexString(Utility.getMd5(randomString));
		int[] utcStrMD5Array = Utility.getBinaryArrayFromHexString(Utility.getMd5(utcStr));
		int[] combined_arr = Utility.interleaveArrays(randomStringMD5Array, utcStrMD5Array);

		int inputs = 256;
		INDArray features = Nd4j.zeros(inputs);

		for (int i = 0; i < inputs; i++) {
			// features.putScalar(new int[] { i }, Math.random() < 0.5 ? 0 : 1);
			features.putScalar(new int[] { i }, combined_arr[i]);
		}
		features = features.reshape(new long[] { 1, 256 });

		INDArray output = model.output(features);
		double mean = output.mean().getDouble(0);
		System.out.println("mean=" + mean);

		double[] raw_output = output.toDoubleVector();

		int raw_output_len = raw_output.length;
		int[] raw_bits = new int[raw_output_len];
		for (int i = 0; i < raw_output_len; i++) {
			raw_bits[i] = raw_output[i] > mean ? 1 : 0;
			// System.out.print(raw_bits[i]);
		}
		String aesKey = Utility.getHexStringFromBinaryArray(raw_bits);
		return aesKey;
	}
}
