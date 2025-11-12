/**
 * Configuration loader and validator
 */

import type { Config } from './types';

export class ConfigLoader {
  /**
   * Load configuration from a file
   */
  static async loadFromFile(filePath: string): Promise<Config> {
    try {
      const file = Bun.file(filePath);
      const content = await file.text();
      const config = JSON.parse(content);

      this.validateConfig(config);

      return config;
    } catch (error) {
      throw new Error(`Failed to load config from ${filePath}: ${error}`);
    }
  }

  /**
   * Load configuration from environment variables and object
   */
  static loadFromEnv(configOverrides?: Partial<Config>): Config {
    const config: Config = {
      newRelic: {
        apiKey: process.env.NEW_RELIC_API_KEY || '',
        accountId: process.env.NEW_RELIC_ACCOUNT_ID || '',
        pollingIntervalMs: process.env.POLLING_INTERVAL_MS
          ? parseInt(process.env.POLLING_INTERVAL_MS, 10)
          : 10000,
      },
      backend: {
        endpoint: process.env.GRAPHQL_ENDPOINT || 'http://localhost:4000/graphql',
        headers: process.env.GRAPHQL_HEADERS
          ? JSON.parse(process.env.GRAPHQL_HEADERS)
          : {},
      },
      mappings: [],
      nrqlQuery: process.env.NRQL_QUERY,
      ...configOverrides,
    };

    this.validateConfig(config);

    return config;
  }

  /**
   * Validate configuration
   */
  private static validateConfig(config: any): asserts config is Config {
    if (!config.newRelic?.apiKey) {
      throw new Error('Missing required config: newRelic.apiKey');
    }

    if (!config.newRelic?.accountId) {
      throw new Error('Missing required config: newRelic.accountId');
    }

    if (!config.backend?.endpoint) {
      throw new Error('Missing required config: backend.endpoint');
    }

    if (!Array.isArray(config.mappings)) {
      throw new Error('Config mappings must be an array');
    }

    for (const mapping of config.mappings) {
      if (!mapping.name) {
        throw new Error('Each mapping must have a name');
      }

      if (!Array.isArray(mapping.filters)) {
        throw new Error(`Mapping "${mapping.name}" must have filters array`);
      }

      if (!mapping.mutation) {
        throw new Error(`Mapping "${mapping.name}" must have a mutation`);
      }

      if (!Array.isArray(mapping.extractors)) {
        throw new Error(`Mapping "${mapping.name}" must have extractors array`);
      }
    }
  }

  /**
   * Create a sample configuration file
   */
  static async createSampleConfig(filePath: string): Promise<void> {
    const sampleConfig: Config = {
      newRelic: {
        apiKey: 'YOUR_NEW_RELIC_API_KEY',
        accountId: 'YOUR_ACCOUNT_ID',
        pollingIntervalMs: 10000,
      },
      backend: {
        endpoint: 'http://localhost:4000/graphql',
        headers: {
          'Authorization': 'Bearer YOUR_TOKEN',
        },
      },
      nrqlQuery: "SELECT * FROM Log WHERE service = 'my-service'",
      mappings: [
        {
          name: 'user-signup',
          filters: [
            {
              field: 'message',
              operator: 'contains',
              value: 'User signed up',
            },
            {
              field: 'attributes.userId',
              operator: 'exists',
            },
          ],
          mutation: `
            mutation CreateUser($userId: ID!, $email: String!, $name: String) {
              createUser(userId: $userId, email: $email, name: $name) {
                id
                email
              }
            }
          `,
          extractors: [
            {
              sourcePath: 'attributes.userId',
              targetField: 'userId',
            },
            {
              sourcePath: 'attributes.email',
              targetField: 'email',
              transform: 'lowercase',
            },
            {
              sourcePath: 'attributes.name',
              targetField: 'name',
              defaultValue: 'Unknown',
            },
          ],
        },
      ],
    };

    await Bun.write(filePath, JSON.stringify(sampleConfig, null, 2));
    console.log(`Sample config created at ${filePath}`);
  }
}
