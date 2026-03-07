export async function loadFirebaseRuntimeConfig() {
  if (globalThis.__FOUNDUPS_FIREBASE_CONFIG__) {
    return globalThis.__FOUNDUPS_FIREBASE_CONFIG__;
  }

  const metaConfig = document.querySelector('meta[name="foundups-firebase-config"]');
  if (metaConfig?.content) {
    return JSON.parse(metaConfig.content);
  }

  const response = await fetch('/__/firebase/init.json', { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(
      `Firebase runtime config unavailable (${response.status}). ` +
      'Serve this site from Firebase Hosting or inject __FOUNDUPS_FIREBASE_CONFIG__.'
    );
  }

  return await response.json();
}
