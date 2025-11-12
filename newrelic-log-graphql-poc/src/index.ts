/**
 * Main entry point for the New Relic Log to GraphQL POC
 */

import 'dotenv/config';
import { LogReplayOrchestrator } from './orchestrator';
import { ConfigLoader } from './config-loader';

async function main() {
  console.log('=== New Relic Log to GraphQL POC ===\n');

  // Parse command line arguments
  const args = process.argv.slice(2);
  const command = args[0];

  if (command === 'init') {
    // Create sample config
    const configPath = args[1] || './config.json';
    await ConfigLoader.createSampleConfig(configPath);
    console.log(`\nSample configuration created at: ${configPath}`);
    console.log('Please edit this file with your settings and run: bun run start');
    return;
  }

  // Load configuration
  let config;
  try {
    if (args.includes('--config')) {
      const configIndex = args.indexOf('--config');
      const configPath = args[configIndex + 1];
      console.log(`Loading config from: ${configPath}`);
      config = await ConfigLoader.loadFromFile(configPath);
    } else {
      console.log('Loading config from environment variables');
      config = ConfigLoader.loadFromEnv();
    }
  } catch (error) {
    console.error('Failed to load configuration:', error);
    console.log('\nUsage:');
    console.log('  bun run init [config-path]     - Create sample config');
    console.log('  bun run start --config <path>  - Start with config file');
    console.log('  bun run start                  - Start with env variables');
    console.log('  bun run once --config <path>   - Run once (testing)');
    process.exit(1);
  }

  // Create orchestrator
  const orchestrator = new LogReplayOrchestrator(config);

  // Handle run mode
  if (command === 'once') {
    // Run once for testing
    await orchestrator.runOnce();
  } else {
    // Start continuous polling
    orchestrator.start();

    // Handle graceful shutdown
    process.on('SIGINT', () => {
      console.log('\n\nReceived SIGINT, shutting down...');
      orchestrator.stop();
      process.exit(0);
    });

    process.on('SIGTERM', () => {
      console.log('\n\nReceived SIGTERM, shutting down...');
      orchestrator.stop();
      process.exit(0);
    });
  }
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
