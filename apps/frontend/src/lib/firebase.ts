import { initializeApp, getApps } from "firebase/app";
import { getAuth, GoogleAuthProvider, RecaptchaVerifier, signInWithPhoneNumber, signInWithPopup } from "firebase/auth";

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyACJ3rELV-iuGuDYGVblJI2eQqRQaRAUaA",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "webiscrap.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "webiscrap",
  storageBucket: "webiscrap.firebasestorage.app",
  messagingSenderId: "299695227616",
  appId: "1:299695227616:web:2603a5a4ee86e953e88685",
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
