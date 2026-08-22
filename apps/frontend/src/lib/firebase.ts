import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider, RecaptchaVerifier, signInWithPhoneNumber, signInWithPopup } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "",
};

// Initialize Firebase only if not already initialized
const getFirebaseApp = () => {
  return getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
};

const getFirebaseAuth = () => {
  return getAuth(getFirebaseApp());
};

const getGoogleProvider = () => {
  return new GoogleAuthProvider();
};

export { getFirebaseAuth, getGoogleProvider, RecaptchaVerifier, signInWithPhoneNumber, signInWithPopup };
