/**
 * Firebase Auth for Google sign-in using redirect flow (full-tab navigation to Google accounts).
 * Everything comes from NEXT_PUBLIC_FIREBASE_* env vars, and the SDK is loaded lazily
 * (dynamic import) so it is not part of the initial login bundle.
 */
export function isFirebaseConfigured(): boolean {
  return Boolean(process.env.NEXT_PUBLIC_FIREBASE_API_KEY && process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID);
}

export async function signInWithGoogleRedirect(): Promise<void> {
  if (!isFirebaseConfigured()) {
    throw new Error("Google sign-in is not configured for this deployment. Please use email or continue as guest.");
  }
  const [{ initializeApp, getApps }, { getAuth, GoogleAuthProvider, signInWithRedirect }] = await Promise.all([
    import("firebase/app"),
    import("firebase/auth"),
  ]);
  const app = getApps().length ? getApps()[0] : initializeApp({
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  });
  const auth = getAuth(app);
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });
  await signInWithRedirect(auth, provider);
}

export async function getGoogleRedirectResult(): Promise<string | null> {
  if (!isFirebaseConfigured()) {
    return null;
  }
  const [{ initializeApp, getApps }, { getAuth, getRedirectResult }] = await Promise.all([
    import("firebase/app"),
    import("firebase/auth"),
  ]);
  const app = getApps().length ? getApps()[0] : initializeApp({
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  });
  const auth = getAuth(app);
  const result = await getRedirectResult(auth);
  if (result && result.user) {
    return await result.user.getIdToken();
  }
  return null;
}

export async function signInWithGooglePopup(): Promise<string> {
  if (!isFirebaseConfigured()) {
    throw new Error("Google sign-in is not configured for this deployment. Please use email or continue as guest.");
  }
  const [{ initializeApp, getApps }, { getAuth, GoogleAuthProvider, signInWithPopup }] = await Promise.all([
    import("firebase/app"),
    import("firebase/auth"),
  ]);
  const app = getApps().length ? getApps()[0] : initializeApp({
    apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
    authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  });
  const result = await signInWithPopup(getAuth(app), new GoogleAuthProvider());
  return result.user.getIdToken();
}

export function formatFirebaseAuthError(err: unknown): string {
  const e = err as { code?: string; message?: string } | null;
  switch (e?.code) {
    case "auth/popup-closed-by-user":
    case "auth/cancelled-popup-request":
      return "";
    case "auth/popup-blocked":
      return "Your browser blocked the sign-in popup. Allow popups for this site and try again.";
    case "auth/unauthorized-domain":
      return "This website is not authorised for Google sign-in yet.";
    case "auth/too-many-requests":
      return "Too many attempts. Please try again later or sign in with email.";
    default:
      return e?.message?.includes("Firebase:") ? "Google sign-in is temporarily unavailable. Please use email or continue as guest." : e?.message || "Authentication failed. Please try again.";
  }
}
