import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider, RecaptchaVerifier, signInWithPhoneNumber, signInWithPopup } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "",
};

// Initialize Firebase only if not already initialized
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export { auth, googleProvider, RecaptchaVerifier, signInWithPhoneNumber, signInWithPopup };
