package edu.fyko.java;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.security.NoSuchAlgorithmException;

import org.deeplearning4j.nn.modelimport.keras.KerasModelImport;
import org.deeplearning4j.nn.modelimport.keras.exceptions.InvalidKerasConfigurationException;
import org.deeplearning4j.nn.modelimport.keras.exceptions.UnsupportedKerasConfigurationException;
import org.deeplearning4j.nn.multilayer.MultiLayerNetwork;

/**
 * Testing Class:
 * 
 * Uses ANN models and AES Keys that were created on Remote Server (Google Colab
 * run with TPU) To test for AES Key mismatch.
 * 
 * @author mitra
 *
 */
public class RegenerateAndCompareAesKeysOnRemoteServer {

	private static void testAesKeyMisMatch(String modelName) throws IOException, InvalidKerasConfigurationException,
			UnsupportedKerasConfigurationException, NoSuchAlgorithmException {
		System.out.println("============= START =============");
		System.out.println("Loading " + modelName + " model created on Remote Server...");
		InputStream h5FileStream = RegenerateAndCompareAesKeysOnRemoteServer.class.getClassLoader()
				.getResourceAsStream(modelName + ".h5");
		MultiLayerNetwork model = KerasModelImport.importKerasSequentialModelAndWeights(h5FileStream, false);
		h5FileStream.close();

		System.out.println("Loading Data Samples with AES Keys generated from " + modelName + " model...");
		InputStream dataSamplesSimple = RegenerateAndCompareAesKeysOnRemoteServer.class.getClassLoader()
				.getResourceAsStream(modelName + ".csv");
		InputStreamReader inputStreamReader = new InputStreamReader(dataSamplesSimple, StandardCharsets.UTF_8);
		BufferedReader br = new BufferedReader(inputStreamReader);
		String line = br.readLine();
		System.out.println("Testing AES Keys by re-generating them locally...");
		int aesKeyMisMatchCount = 0;
		int index = 0;
		while ((line = br.readLine()) != null) {
			index++;
			String[] res = line.split(",(?=([^\"]|\"[^\"]*\")*$)");
			String sourceString = Utility.stripQuotes(res[2]);
			long utcSeconds = Long.parseLong(res[4]);
			String aesKeyRemoteServer = Utility.stripQuotes(res[7]);
			String aesKey = Utility.generateAESKey(model, utcSeconds, sourceString);
			if (!aesKeyRemoteServer.equals(aesKey)) {
				aesKeyMisMatchCount++;
				System.out.println("*********");
				System.out.println("AES Key Mismatch Alert...");
				System.out.println("Remote Server AES Key:" + aesKeyRemoteServer);
				System.out.println("Local Machine AES Key:" + aesKey);
				System.out.println("*********");
			}
		}
		br.close();
		inputStreamReader.close();
		dataSamplesSimple.close();
		System.out.println("Result: Out of " + index + " samples produced using " + modelName
				+ " ANN, number of AES Key mismatches = " + aesKeyMisMatchCount);
		System.out.println("Mismatch percentage = " + (float) (aesKeyMisMatchCount * 100) / index);
		System.out.println("============= END =============");
	}

	public static void main(String[] args) throws IOException, InvalidKerasConfigurationException,
			UnsupportedKerasConfigurationException, NoSuchAlgorithmException {
		testAesKeyMisMatch("simple");
		testAesKeyMisMatch("complex");
	}
}