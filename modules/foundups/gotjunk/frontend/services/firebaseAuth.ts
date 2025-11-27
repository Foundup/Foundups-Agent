/**
 * Firebase Authentication Service
 * WSP 98: User identity for cross-device sync
 *
 * Strategy:
 * - Default: Anonymous Auth (zero friction, persistent UID per device)
 * - Upgrade: Google Sign-In for cross-device identity with same Google account
 *
 * Usage:
 * - Call initializeAuth() once on app startup to restore session or anon sign-in
 * - Use getCurrentUserId() when writing ownership to Firestore
 */

import { getAuth, signInAnonymously, signInWithPopup, GoogleAuthProvider, onAuthStateChanged, User } from 'firebase/auth';
import { getFirebaseApp } from './firebaseConfig';

let auth: ReturnType<typeof getAuth> | null = null;
let currentUser: User | null = null;
let authInitialized = false;

/**
 * Initialize Firebase Auth (lazy singleton)
 */
export const getFirebaseAuth = () => {
  if (auth) return auth;

  const app = getFirebaseApp();
  if (!app) return null;

  auth = getAuth(app);
  return auth;
};

/**
 * Get current user UID (or null if not authenticated)
 */
export const getCurrentUserId = (): string | null => {
  return currentUser?.uid || null;
};

/**
 * Get current user object
 */
export const getCurrentUser = (): User | null => {
  return currentUser;
};

/**
 * Sign in anonymously (auto sign-in on first load)
 */
export const signInAnonymous = async (): Promise<User | null> => {
  const authInstance = getFirebaseAuth();
  if (!authInstance) return null;

  try {
    const result = await signInAnonymously(authInstance);
    currentUser = result.user;
    console.log('[Auth] Anonymous sign-in successful:', currentUser.uid);
    return currentUser;
  } catch (error) {
    console.error('[Auth] Anonymous sign-in failed:', error);
    return null;
  }
};

/**
 * Upgrade anonymous account to Google Sign-In (cross-device sync)
 */
export const signInWithGoogle = async (): Promise<User | null> => {
  const authInstance = getFirebaseAuth();
  if (!authInstance) return null;

  try {
    const provider = new GoogleAuthProvider();
    const result = await signInWithPopup(authInstance, provider);
    currentUser = result.user;
    console.log('[Auth] Google sign-in successful:', currentUser.uid);
    return currentUser;
  } catch (error) {
    console.error('[Auth] Google sign-in failed:', error);
    return null;
  }
};

/**
 * Initialize auth and auto-sign-in
 * Call this once on app startup
 */
export const initializeAuth = async (): Promise<User | null> => {
  if (authInitialized) {
    return currentUser;
  }

  const authInstance = getFirebaseAuth();
  if (!authInstance) return null;

  return new Promise((resolve) => {
    const unsubscribe = onAuthStateChanged(authInstance, async (user) => {
      if (user) {
        currentUser = user;
        authInitialized = true;
        console.log('[Auth] Session restored:', user.uid);
        unsubscribe();
        resolve(user);
      } else {
        const anonUser = await signInAnonymous();
        authInitialized = true;
        unsubscribe();
        resolve(anonUser);
      }
    });
  });
};

/**
 * Subscribe to auth state changes
 */
export const onAuthChanged = (callback: (user: User | null) => void) => {
  const authInstance = getFirebaseAuth();
  if (!authInstance) return () => {};

  return onAuthStateChanged(authInstance, (user) => {
    currentUser = user;
    callback(user);
  });
};

/**
 * Sign out
 */
export const signOut = async (): Promise<void> => {
  const authInstance = getFirebaseAuth();
  if (!authInstance) return;

  try {
    await authInstance.signOut();
    currentUser = null;
    console.log('[Auth] Signed out');
  } catch (error) {
    console.error('[Auth] Sign out failed:', error);
  }
};
