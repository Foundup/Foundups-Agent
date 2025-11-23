/**
 * Firebase Configuration for GotJunk FoundUp
 * WSP 98: FoundUps Mesh-Native Architecture Protocol - Layer 2 (Global Index)
 *
 * SECURITY NOTE: Firebase web config is PUBLIC (exposed in client-side code).
 * Security comes from Firestore Security Rules, not hidden config.
 *
 * Project: gen-lang-client-0061781628
 *
 * Environment Variables (set in Cloud Run):
 * - VITE_FIREBASE_API_KEY: Firebase Web API Key
 * - VITE_FIREBASE_APP_ID: Firebase App ID
 */

import { initializeApp, getApps, FirebaseApp } from 'firebase/app';
import { getFirestore, Firestore } from 'firebase/firestore';
import { getStorage, FirebaseStorage } from 'firebase/storage';

// Firebase configuration - Hardcoded for GotJunk PWA
// These are PUBLIC values (Firebase web config is client-side)
// Security is enforced via Firestore Security Rules
const firebaseConfig = {
  apiKey: 'AIzaSyCpvfTJX5nI6UWAPSIPfIIC_wr7AAYkjAo',
  authDomain: 'gen-lang-client-0061781628.firebaseapp.com',
  projectId: 'gen-lang-client-0061781628',
  storageBucket: 'gen-lang-client-0061781628.firebasestorage.app',
  messagingSenderId: '56566376153',
  appId: '1:56566376153:web:3ac1a0798ff20b10ebc0c8',
  measurementId: 'G-65KCHXR5VL',
};

// Singleton instances
let app: FirebaseApp | null = null;
let db: Firestore | null = null;
let storage: FirebaseStorage | null = null;

/**
 * Check if Firebase is properly configured
 * Always true now that config is hardcoded
 */
export const isFirebaseConfigured = (): boolean => {
  return true; // Config is hardcoded - always available
};

/**
 * Initialize Firebase app (lazy singleton)
 */
export const getFirebaseApp = (): FirebaseApp | null => {
  if (!isFirebaseConfigured()) {
    console.warn('[Firebase] Not configured - set VITE_FIREBASE_API_KEY and VITE_FIREBASE_APP_ID');
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
