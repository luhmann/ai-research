/**
 * Main orchestrator that coordinates log polling, filtering, and GraphQL execution
 */

import { NewRelicClient } from './newrelic-client';
import { FilterEngine } from './filter-engine';
import { BackendGraphQLClient } from './graphql-client';
import type { Config, LogEntry } from './types';

export class LogReplayOrchestrator {
  private newRelicClient: NewRelicClient;
  private filterEngine: FilterEngine;
  private graphqlClient: BackendGraphQLClient;
  private config: Config;
  private stopPolling?: () => void;

  constructor(config: Config) {
    this.config = config;
    this.newRelicClient = new NewRelicClient(config.newRelic);
    this.filterEngine = new FilterEngine();
    this.graphqlClient = new BackendGraphQLClient(config.backend);
  }

  /**
   * Process a batch of logs
   */
  private async processLogs(logs: LogEntry[]): Promise<void> {
    console.log(`\n[Orchestrator] Processing ${logs.length} logs...`);

    // Filter and extract data from logs
    const matches = this.filterEngine.processLogs(logs, this.config.mappings);

    if (matches.length === 0) {
      console.log('[Orchestrator] No matching logs found');
      return;
    }

    console.log(`[Orchestrator] Found ${matches.length} matches, executing mutations...`);

    // Execute mutations
    const mutations = matches.map(match => ({
      mutation: match.mapping.mutation,
      variables: match.variables,
    }));

    const results = await this.graphqlClient.executeMutations(mutations);

    // Log results
    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;

    console.log(`[Orchestrator] Mutations complete: ${successCount} succeeded, ${failureCount} failed`);

    if (failureCount > 0) {
      console.log('[Orchestrator] Failed mutations:');
      results.forEach((result, index) => {
        if (!result.success) {
          console.error(`  - Mutation ${index + 1}:`, result.error);
        }
      });
    }
  }

  /**
   * Start the log replay process
   */
  start(): void {
    console.log('[Orchestrator] Starting log replay...');
    console.log(`  - New Relic Account: ${this.config.newRelic.accountId}`);
    console.log(`  - Backend: ${this.config.backend.endpoint}`);
    console.log(`  - Polling interval: ${this.config.newRelic.pollingIntervalMs || 10000}ms`);
    console.log(`  - Mappings: ${this.config.mappings.length}`);

    this.stopPolling = this.newRelicClient.startPolling(
      (logs) => this.processLogs(logs),
      this.config.nrqlQuery
    );

    console.log('[Orchestrator] Log replay started. Press Ctrl+C to stop.');
  }

  /**
   * Stop the log replay process
   */
  stop(): void {
    console.log('[Orchestrator] Stopping log replay...');

    if (this.stopPolling) {
      this.stopPolling();
      this.stopPolling = undefined;
    }

    console.log('[Orchestrator] Log replay stopped.');
  }

  /**
   * Run once without continuous polling (useful for testing)
   */
  async runOnce(): Promise<void> {
    console.log('[Orchestrator] Running one-time log fetch...');

    const logs = await this.newRelicClient.queryLogs(this.config.nrqlQuery);
    await this.processLogs(logs);

    console.log('[Orchestrator] One-time run complete.');
  }
}
