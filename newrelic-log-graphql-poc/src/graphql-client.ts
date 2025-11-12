/**
 * GraphQL client for executing mutations against local backend
 */

import { GraphQLClient } from 'graphql-request';
import type { GraphQLBackendConfig } from './types';

export class BackendGraphQLClient {
  private client: GraphQLClient;

  constructor(config: GraphQLBackendConfig) {
    this.client = new GraphQLClient(config.endpoint, {
      headers: config.headers || {},
    });
  }

  /**
   * Execute a GraphQL mutation with variables
   */
  async executeMutation(
    mutation: string,
    variables: Record<string, any>
  ): Promise<any> {
    try {
      console.log(`[GraphQL] Executing mutation with variables:`, JSON.stringify(variables, null, 2));

      const result = await this.client.request(mutation, variables);

      console.log(`[GraphQL] Mutation successful`);

      return result;
    } catch (error) {
      console.error(`[GraphQL] Mutation failed:`, error);
      throw error;
    }
  }

  /**
   * Execute multiple mutations in parallel
   */
  async executeMutations(
    mutations: Array<{ mutation: string; variables: Record<string, any> }>
  ): Promise<Array<{ success: boolean; result?: any; error?: any }>> {
    const promises = mutations.map(async ({ mutation, variables }) => {
      try {
        const result = await this.executeMutation(mutation, variables);
        return { success: true, result };
      } catch (error) {
        return { success: false, error };
      }
    });

    return Promise.all(promises);
  }
}
