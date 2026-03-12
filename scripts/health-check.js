#!/usr/bin/env node

const http = require('http');
const https = require('https');
const { execSync, spawn } = require('child_process');

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const HEALTH_ENDPOINT = `${BACKEND_URL}/health`;
const MAX_RETRIES = 30;
const INITIAL_RETRY_INTERVAL = 2000; // milliseconds
const TIMEOUT_PER_CHECK = 5000; // milliseconds

function checkHealth(retryCount = 0, currentInterval = INITIAL_RETRY_INTERVAL) {
  return new Promise((resolve, reject) => {
    const url = new URL(HEALTH_ENDPOINT);

    // Choose http or https based on protocol
    const client = url.protocol === 'https:' ? https : http;

    const options = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      method: 'GET',
      timeout: TIMEOUT_PER_CHECK
    };

    const req = client.request(options, (res) => {
      if (res.statusCode === 200) {
        console.log('✅ Backend health check passed!');
        // Try to read response data
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            const jsonData = JSON.parse(data);
            console.log('📍 Response:', jsonData);
          } catch (e) {
            console.log('📍 Response text:', data.substring(0, 200) + (data.length > 200 ? '...' : ''));
          }
          resolve(true);
        });
      } else if (res.statusCode === 404) {
        console.log(`❌ Health endpoint not found: ${HEALTH_ENDPOINT}`);
        if (retryCount < MAX_RETRIES) {
          const nextInterval = Math.min(currentInterval * 1.1, 10000); // Cap at 10 seconds
          console.log(`⏳ Retrying in ${(nextInterval / 1000).toFixed(1)}s... (${retryCount + 1}/${MAX_RETRIES})`);
          setTimeout(() => checkHealth(retryCount + 1, nextInterval).then(resolve).catch(reject), nextInterval);
        } else {
          reject(new Error('Backend health check failed after maximum retries'));
        }
      } else {
        console.log(`❌ Backend health check failed with status: ${res.statusCode}`);
        if (retryCount < MAX_RETRIES) {
          const nextInterval = Math.min(currentInterval * 1.1, 10000); // Cap at 10 seconds
          console.log(`⏳ Retrying in ${(nextInterval / 1000).toFixed(1)}s... (${retryCount + 1}/${MAX_RETRIES})`);
          setTimeout(() => checkHealth(retryCount + 1, nextInterval).then(resolve).catch(reject), nextInterval);
        } else {
          reject(new Error('Backend health check failed after maximum retries'));
        }
      }
    });

    req.on('error', (err) => {
      console.log(`⚠️  Backend not reachable yet: ${err.message}`);
      if (retryCount < MAX_RETRIES) {
        const nextInterval = Math.min(currentInterval * 1.1, 10000); // Cap at 10 seconds
        console.log(`⏳ Retrying in ${(nextInterval / 1000).toFixed(1)}s... (${retryCount + 1}/${MAX_RETRIES})`);
        setTimeout(() => checkHealth(retryCount + 1, nextInterval).then(resolve).catch(reject), nextInterval);
      } else {
        reject(new Error('Backend health check failed after maximum retries'));
      }
    });

    req.on('timeout', () => {
      console.log('⏰ Backend health check timed out');
      req.destroy();
      if (retryCount < MAX_RETRIES) {
        const nextInterval = Math.min(currentInterval * 1.1, 10000); // Cap at 10 seconds
        console.log(`⏳ Retrying in ${(nextInterval / 1000).toFixed(1)}s... (${retryCount + 1}/${MAX_RETRIES})`);
        setTimeout(() => checkHealth(retryCount + 1, nextInterval).then(resolve).catch(reject), nextInterval);
      } else {
        reject(new Error('Backend health check failed after maximum retries'));
      }
    });

    req.end();
  });
}

async function main() {
  console.log('🔍 Starting health check process...');
  console.log(`📍 Health endpoint: ${HEALTH_ENDPOINT}`);
  console.log(`📍 Maximum retries: ${MAX_RETRIES}`);
  console.log(`📍 Initial retry interval: ${(INITIAL_RETRY_INTERVAL / 1000)}s`);
  console.log(`📍 Timeout per check: ${(TIMEOUT_PER_CHECK / 1000)}s`);

  try {
    await checkHealth();
    console.log('🎉 Backend is healthy and ready!');

    // Execute the original command that was passed to this script
    if (process.argv.length > 2) {
      const command = process.argv.slice(2).join(' ');
      console.log(`🚀 Executing command: ${command}`);

      try {
        const child = execSync(command, { stdio: 'inherit' });
        console.log('✅ Command completed successfully');
        process.exit(0);
      } catch (error) {
        console.error('💥 Command failed:', error.message);
        process.exit(error.status || 1);
      }
    } else {
      console.log('ℹ️  Backend is healthy, no command to execute');
    }
  } catch (error) {
    console.error('💥 Backend health check failed:', error.message);
    console.error('❌ Exiting with code 1');
    process.exit(1);
  }
}

main().catch(console.error);