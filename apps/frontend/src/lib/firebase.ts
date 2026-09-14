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

export function formatFirebaseAuthError(err: any): string {
  if (!err) return "Authentication failed";
  const code = err.code || "";
  switch (code) {
    case "auth/configuration-not-found":
    case "auth/operation-not-allowed":
      return "Google Sign-In is not enabled in Firebase Console. Please sign in with Email & Password or Continue as Guest.";
    case "auth/unauthorized-domain":
      return "This domain is not authorized in Firebase Console. Please add webiscrap.vercel.app to Authorized Domains.";
    case "auth/popup-blocked":
      return "Popup was blocked by your browser. Please allow popups for this site.";
    case "auth/popup-closed-by-user":
      return "";
    case "auth/invalid-phone-number":
      return "The phone number entered is invalid. Please include your country code (e.g. +91...).";
    case "auth/too-many-requests":
      return "Too many attempts. Please try again later or sign in with Email & Password.";
    default:
      if (err.message && err.message.includes("Firebase:")) {
        return "Authentication provider temporarily unavailable. Please use Email & Password or Continue as Guest.";
      }
      return err.message || "Authentication failed. Please try again.";
  }
}

export { getFirebaseAuth, getGoogleProvider, RecaptchaVerifier, signInWithPhoneNumber, signInWithPopup };
