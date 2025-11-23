import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { execSync } from 'child_process';

// Get git commit hash at build time
const getGitCommitHash = () => {
  try {
    return execSync('git rev-parse --short HEAD').toString().trim();
  } catch {
    return 'dev';
  }
};

export default defineConfig(({ mode }) => {
    // Load .env from project root (4 levels up)
    const envDir = path.resolve(__dirname, '../../../../');
    const env = loadEnv(mode, envDir, '');
    const commitHash = getGitCommitHash();

    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [
        react()
      ],
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY_GotJunk),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY_GotJunk),
        '__COMMIT_HASH__': JSON.stringify(commitHash),
        '__BUILD_TIME__': JSON.stringify(new Date().toISOString())
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      },
      optimizeDeps: {
        include: ['leaflet', 'react-leaflet']
      },
      build: {
        commonjsOptions: {
          transformMixedEsModules: true
        }
      }
    };
});
