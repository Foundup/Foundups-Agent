/**
 * Firebase Configuration for GotJunk FoundUp
 * WSP 98: FoundUps Mesh-Native Architecture Protocol - Layer 2 (Global Index)
 *
 * SECURITY NOTE: Firebase web config is PUBLIC (exposed in client-side code).
 * Security comes from Firestore Security Rules, not hidden config.
 *
 * Project: gen-lang-client-0061781628
 *
 * Environment Variables (set in .env or Cloud Run):
 * - VITE_FIREBASE_API_KEY: Firebase Web API Key
 * - VITE_FIREBASE_APP_ID: Firebase App ID
 * - VITE_FIREBASE_SENDER_ID: Firebase Messaging Sender ID
 */

import { initializeApp, getApps, FirebaseApp } from 'firebase/app';
import { getFirestore, Firestore } from 'firebase/firestore';
import { getStorage, FirebaseStorage } from 'firebase/storage';

// Firebase configuration from environment variables
// Set these in .env file (gitignored) or Cloud Run secrets
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || '',
  authDomain: 'gen-lang-client-0061781628.firebaseapp.com',
  projectId: 'gen-lang-client-0061781628',
  storageBucket: 'gen-lang-client-0061781628.firebasestorage.app',
  messagingSenderId: import.meta.env.VITE_FIREBASE_SENDER_ID || '',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '',
  measurementId: 'G-65KCHXR5VL',
};

// Singleton instances
let app: FirebaseApp | null = null;
let db: Firestore | null = null;
let storage: FirebaseStorage | null = null;

/**
 * Check if Firebase is properly configured
 * Requires VITE_FIREBASE_API_KEY and VITE_FIREBASE_APP_ID env vars
 */
export const isFirebaseConfigured = (): boolean => {
  return !!(firebaseConfig.apiKey && firebaseConfig.appId);
};

/**
 * Initialize Firebase app (lazy singleton)
 */
export const getFirebaseApp = (): FirebaseApp | null => {
  if (!isFirebaseConfigured()) {
    console.warn('[Firebase] Not configured - set VITE_FIREBASE_API_KEY and VITE_FIREBASE_APP_ID in .env');
    return null;
  }

  if (!app && getApps().length === 0) {
    try {
      app = initializeApp(firebaseConfig);
      console.log('[Firebase] Initialized successfully');
    } catch (error) {
      console.error('[Firebase] Initialization failed:', error);
      return null;
    }
  } else if (!app) {
    app = getApps()[0];
  }

  return app;
};

/**
 * Get Firestore instance (Layer 2: Global Index)
 */
export const getFirestoreDb = (): Firestore | null => {
  if (db) return db;

  const firebaseApp = getFirebaseApp();
  if (!firebaseApp) return null;

  try {
    db = getFirestore(firebaseApp);
    console.log('[Firestore] Connected to global index');
    return db;
  } catch (error) {
    console.error('[Firestore] Connection failed:', error);
    return null;
  }
};

/**
 * Get Firebase Storage instance (for blob sync)
 */
export const getFirebaseStorage = (): FirebaseStorage | null => {
  if (storage) return storage;

  const firebaseApp = getFirebaseApp();
  if (!firebaseApp) return null;

  try {
    storage = getStorage(firebaseApp);
    console.log('[Firebase Storage] Connected');
    return storage;
  } catch (error) {
    console.error('[Firebase Storage] Connection failed:', error);
    return null;
  }
};

// Export config for debugging
export const getFirebaseConfig = () => ({
  projectId: firebaseConfig.projectId,
  authDomain: firebaseConfig.authDomain,
  isConfigured: isFirebaseConfigured(),
});
