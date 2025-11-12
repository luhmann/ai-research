/**
 * Filter and data extraction engine for log entries
 */

import type { LogEntry, FilterRule, ExtractorRule, MutationMapping } from './types';

export class FilterEngine {
  /**
   * Get a nested value from an object using a path like "attributes.userId"
   */
  private getNestedValue(obj: any, path: string): any {
    const parts = path.split('.');
    let current = obj;

    for (const part of parts) {
      if (current === null || current === undefined) {
        return undefined;
      }
      current = current[part];
    }

    return current;
  }

  /**
   * Check if a single filter rule matches a log entry
   */
  private matchesFilter(log: LogEntry, filter: FilterRule): boolean {
    const value = this.getNestedValue(log, filter.field);

    switch (filter.operator) {
      case 'exists':
        return value !== undefined && value !== null;

      case 'equals':
        return value === filter.value;

      case 'contains':
        if (typeof value === 'string' && typeof filter.value === 'string') {
          return value.includes(filter.value);
        }
        if (Array.isArray(value)) {
          return value.includes(filter.value);
        }
        return false;

      case 'regex':
        if (typeof value === 'string' && typeof filter.value === 'string') {
          const regex = new RegExp(filter.value);
          return regex.test(value);
        }
        return false;

      case 'gt':
        return typeof value === 'number' && value > filter.value;

      case 'lt':
        return typeof value === 'number' && value < filter.value;

      default:
        console.warn(`Unknown filter operator: ${filter.operator}`);
        return false;
    }
  }

  /**
   * Check if all filter rules match a log entry
   */
  private matchesAllFilters(log: LogEntry, filters: FilterRule[]): boolean {
    return filters.every(filter => this.matchesFilter(log, filter));
  }

  /**
   * Apply transformation to a value
   */
  private applyTransform(value: any, transform?: string): any {
    if (!transform || value === null || value === undefined) {
      return value;
    }

    switch (transform) {
      case 'lowercase':
        return typeof value === 'string' ? value.toLowerCase() : value;

      case 'uppercase':
        return typeof value === 'string' ? value.toUpperCase() : value;

      case 'trim':
        return typeof value === 'string' ? value.trim() : value;

      case 'parseInt':
        return parseInt(String(value), 10);

      case 'parseFloat':
        return parseFloat(String(value));

      case 'json':
        return typeof value === 'string' ? JSON.parse(value) : value;

      default:
        console.warn(`Unknown transform: ${transform}`);
        return value;
    }
  }

  /**
   * Extract data from a log entry based on extractor rules
   */
  private extractData(log: LogEntry, extractors: ExtractorRule[]): Record<string, any> {
    const result: Record<string, any> = {};

    for (const extractor of extractors) {
      let value = this.getNestedValue(log, extractor.sourcePath);

      // Use default value if source is missing
      if (value === undefined || value === null) {
        if (extractor.defaultValue !== undefined) {
          value = extractor.defaultValue;
        } else {
          continue; // Skip this field
        }
      }

      // Apply transformation
      value = this.applyTransform(value, extractor.transform);

      result[extractor.targetField] = value;
    }

    return result;
  }

  /**
   * Process a log entry and find matching mappings
   * Returns array of { mapping, variables } for each match
   */
  processLog(log: LogEntry, mappings: MutationMapping[]): Array<{
    mapping: MutationMapping;
    variables: Record<string, any>;
  }> {
    const matches: Array<{ mapping: MutationMapping; variables: Record<string, any> }> = [];

    for (const mapping of mappings) {
      // Check if log matches all filters
      if (this.matchesAllFilters(log, mapping.filters)) {
        // Extract data for mutation variables
        const variables = this.extractData(log, mapping.extractors);

        matches.push({
          mapping,
          variables,
        });

        console.log(`[Filter] Log matched mapping "${mapping.name}"`);
      }
    }

    return matches;
  }

  /**
   * Process multiple log entries
   */
  processLogs(logs: LogEntry[], mappings: MutationMapping[]): Array<{
    log: LogEntry;
    mapping: MutationMapping;
    variables: Record<string, any>;
  }> {
    const allMatches: Array<{
      log: LogEntry;
      mapping: MutationMapping;
      variables: Record<string, any>;
    }> = [];

    for (const log of logs) {
      const matches = this.processLog(log, mappings);

      for (const match of matches) {
        allMatches.push({
          log,
          ...match,
        });
      }
    }

    console.log(`[Filter] Processed ${logs.length} logs, found ${allMatches.length} matches`);

    return allMatches;
  }
}
