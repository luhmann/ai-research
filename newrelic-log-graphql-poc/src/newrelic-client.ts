/**
 * New Relic NerdGraph client for querying logs
 */

import type { NewRelicConfig, LogEntry } from './types';

export class NewRelicClient {
  private config: NewRelicConfig;
  private lastQueryTimestamp: number;
  private apiEndpoint: string;

  constructor(config: NewRelicConfig) {
    this.config = config;
    this.apiEndpoint = config.apiEndpoint || 'https://api.newrelic.com/graphql';
    // Start from 5 minutes ago by default
    this.lastQueryTimestamp = Date.now() - (5 * 60 * 1000);
  }

  /**
   * Query logs from New Relic using NerdGraph (GraphQL API)
   */
  async queryLogs(nrqlQuery?: string): Promise<LogEntry[]> {
    const currentTime = Date.now();

    // Build NRQL query with timestamp filter
    const baseQuery = nrqlQuery || 'SELECT * FROM Log';
    const timestampFilter = `timestamp > ${this.lastQueryTimestamp}`;

    // Construct the full NRQL query
    const fullQuery = baseQuery.includes('WHERE')
      ? `${baseQuery} AND ${timestampFilter}`
      : `${baseQuery} WHERE ${timestampFilter}`;

    // Add ORDER BY and LIMIT
    const finalQuery = `${fullQuery} ORDER BY timestamp ASC LIMIT 1000`;

    console.log(`[NewRelic] Querying logs: ${finalQuery}`);

    // NerdGraph query structure
    const graphqlQuery = {
      query: `
        query($accountId: Int!, $nrql: Nrql!) {
          actor {
            account(id: $accountId) {
              nrql(query: $nrql) {
                results
              }
            }
          }
        }
      `,
      variables: {
        accountId: parseInt(this.config.accountId),
        nrql: finalQuery
      }
    };

    try {
      const response = await fetch(this.apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'API-Key': this.config.apiKey,
        },
        body: JSON.stringify(graphqlQuery),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`New Relic API error: ${response.status} - ${errorText}`);
      }

      const result = await response.json();

      if (result.errors) {
        throw new Error(`GraphQL errors: ${JSON.stringify(result.errors)}`);
      }

      const logs = result.data?.actor?.account?.nrql?.results || [];

      console.log(`[NewRelic] Retrieved ${logs.length} log entries`);

      // Update the last query timestamp to the latest log timestamp, or current time if no logs
      if (logs.length > 0) {
        const latestTimestamp = Math.max(...logs.map((log: any) => log.timestamp || 0));
        this.lastQueryTimestamp = latestTimestamp + 1; // Add 1ms to avoid duplicates
      } else {
        this.lastQueryTimestamp = currentTime;
      }

      return logs as LogEntry[];
    } catch (error) {
      console.error('[NewRelic] Error querying logs:', error);
      throw error;
    }
  }

  /**
   * Start polling for logs at the configured interval
   */
  startPolling(
    onLogs: (logs: LogEntry[]) => void | Promise<void>,
    nrqlQuery?: string
  ): () => void {
    const intervalMs = this.config.pollingIntervalMs || 10000; // Default 10 seconds

    console.log(`[NewRelic] Starting log polling every ${intervalMs}ms`);

    const poll = async () => {
      try {
        const logs = await this.queryLogs(nrqlQuery);
        if (logs.length > 0) {
          await onLogs(logs);
        }
      } catch (error) {
        console.error('[NewRelic] Polling error:', error);
      }
    };

    // Do initial poll
    poll();

    // Set up interval
    const intervalId = setInterval(poll, intervalMs);

    // Return cleanup function
    return () => {
      console.log('[NewRelic] Stopping log polling');
      clearInterval(intervalId);
    };
  }
}
