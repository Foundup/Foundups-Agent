#!/usr/bin/env node
/**
 * Get Firebase Web Config for GotJunk
 *
 * This script uses the Firebase Admin SDK to list web apps and get their config.
 *
 * Prerequisites:
 *   1. Set GOOGLE_APPLICATION_CREDENTIALS to a service account JSON file
 *      OR run: gcloud auth application-default login
 *   2. npm install firebase-admin
 *
 * Usage: node get_firebase_config.js
 */

const { execSync } = require('child_process');

const PROJECT_ID = 'gen-lang-client-0061781628';

console.log('==========================================');
console.log('Firebase Config Helper for GotJunk');
console.log(`Project: ${PROJECT_ID}`);
console.log('==========================================');
console.log('');
console.log('To get your Firebase Web Config, run:');
console.log('');
console.log('  firebase apps:sdkconfig WEB --project=' + PROJECT_ID);
console.log('');
console.log('Or visit:');
console.log(`  https://console.firebase.google.com/project/${PROJECT_ID}/settings/general`);
console.log('');
console.log('Then add to your .env file:');
console.log('');
console.log('  VITE_FIREBASE_API_KEY=<apiKey from config>');
console.log('  VITE_FIREBASE_APP_ID=<appId from config>');
console.log('  VITE_FIREBASE_SENDER_ID=<messagingSenderId from config>');
console.log('');
console.log('==========================================');

// Try to run firebase CLI if available
try {
    console.log('Attempting to get config via Firebase CLI...');
    console.log('');
    const output = execSync(`firebase apps:sdkconfig WEB --project=${PROJECT_ID}`, {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'pipe']
    });
    console.log('Firebase Web Config:');
    console.log(output);
} catch (error) {
    console.log('Firebase CLI not available or not authenticated.');
    console.log('Please run: firebase login');
    console.log('Then retry this script.');
}
