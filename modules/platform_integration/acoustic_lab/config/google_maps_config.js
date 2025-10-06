// Google Maps API Configuration
// Copy this file to your web server and update the API key

// Replace 'YOUR_GOOGLE_MAPS_API_KEY' with your actual Google Maps API key
// Get your key from: https://console.cloud.google.com/google/maps-apis

const GOOGLE_MAPS_CONFIG = {
    apiKey: 'YOUR_GOOGLE_MAPS_API_KEY',
    libraries: ['places'],
    callback: 'initMap',
    version: 'weekly',

    // Optional: Restrict to specific domains for security
    // Add this to your Google Cloud Console API key restrictions
    allowedDomains: [
        'localhost',
        '127.0.0.1',
        'your-domain.com'
    ]
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GOOGLE_MAPS_CONFIG;
}
