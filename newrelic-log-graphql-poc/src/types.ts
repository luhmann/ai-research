/**
 * Type definitions for the New Relic Log to GraphQL POC
 */

export interface NewRelicConfig {
  apiKey: string;
  accountId: string;
  apiEndpoint?: string;
  pollingIntervalMs?: number;
}

export interface GraphQLBackendConfig {
  endpoint: string;
  headers?: Record<string, string>;
}

export interface LogEntry {
  timestamp: number;
  message: string;
  attributes: Record<string, any>;
  [key: string]: any;
}

export interface FilterRule {
  // Field to match against (supports nested paths like "attributes.userId")
  field: string;
  // Operator: equals, contains, regex, exists
  operator: 'equals' | 'contains' | 'regex' | 'exists' | 'gt' | 'lt';
  // Value to match (not needed for 'exists' operator)
  value?: any;
}

export interface ExtractorRule {
  // Source field path in log entry
  sourcePath: string;
  // Target field name in GraphQL mutation variables
  targetField: string;
  // Optional transformation function name
  transform?: 'lowercase' | 'uppercase' | 'trim' | 'parseInt' | 'parseFloat' | 'json';
  // Optional default value if source is missing
  defaultValue?: any;
}

export interface MutationMapping {
  // Name/identifier for this mapping
  name: string;
  // Filter rules - ALL must match for this mapping to apply
  filters: FilterRule[];
  // GraphQL mutation string
  mutation: string;
  // How to extract and map data from log to mutation variables
  extractors: ExtractorRule[];
}

export interface Config {
  newRelic: NewRelicConfig;
  backend: GraphQLBackendConfig;
  mappings: MutationMapping[];
  // NRQL query to fetch logs (optional, defaults to all logs)
  nrqlQuery?: string;
}
