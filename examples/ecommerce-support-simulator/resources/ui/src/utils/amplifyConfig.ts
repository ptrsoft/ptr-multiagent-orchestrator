import { Amplify, type ResourcesConfig } from 'aws-amplify';
import { fetchAuthSession } from 'aws-amplify/auth';

let awsExports: ResourcesConfig;

export async function configureAmplify(): Promise<void> {
  if (!awsExports) {
    try {
      const awsExportsUrl = new URL('/aws-exports.json', window.location.href).toString();
      console.log("Fetching from:", awsExportsUrl);
      const response = await fetch(awsExportsUrl);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      awsExports = await response.json();
      console.log("Fetched AWS exports:", awsExports);
    } catch (error) {
      console.error("Failed to fetch aws-exports.json:", error);
      throw error;
    }
  }

  if (!awsExports) {
    throw new Error("AWS exports configuration is not available");
  }

  Amplify.configure(awsExports);
}

export async function getAuthToken(): Promise<string | undefined> {
  try {
    console.log("Fetching auth token");
    const session = await fetchAuthSession();
    return session.tokens?.idToken?.toString();
  } catch (error) {
    console.error("Error getting auth token:", error);
    throw error;
  }
}

export async function getAwsExports(): Promise<ResourcesConfig> {
  if (!awsExports) {
    await configureAmplify();
  }
  return awsExports;
}