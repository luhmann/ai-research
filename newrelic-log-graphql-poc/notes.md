# New Relic Log to GraphQL POC - Development Notes

## Objective
Build a POC that:
1. Tails a log stream from New Relic
2. Filters specific messages
3. Extracts info from log messages and metadata
4. Maps them to GraphQL mutations
5. Fires mutations against a local backend

## Progress Log

### Initial Setup
- Created project folder: `newrelic-log-graphql-poc`
- Starting research on New Relic Logs API

## Research Notes

### New Relic Logs API
- **NerdGraph**: New Relic's GraphQL API (https://api.newrelic.com/graphql)
- **Authentication**: Requires API key (user key or license key)
- **NRQL Queries**: Can query logs using NRQL (New Relic Query Language)
- **Live Tail**: UI feature exists, but for programmatic access we'll use NerdGraph with polling
- **Query Structure**:
  ```graphql
  {
    actor {
      account(id: $accountId) {
        nrql(query: $nrqlQuery, timeout: 5) {
          results
        }
      }
    }
  }
  ```

### Key Findings
- NerdGraph supports querying logs via NRQL
- Can do cross-account querying
- Supports asynchronous queries for long-running operations
- For "tailing", we'll implement polling with timestamp tracking

### Architecture Decision
- Will use NerdGraph to poll for new logs (query with timestamp filter)
- Store last seen timestamp to get only new logs
- Parse and filter log messages
- Extract data and map to GraphQL mutations
- Send mutations to local backend

## Implementation Details

### Components Built

1. **newrelic_client.py** - New Relic NerdGraph API client
   - Queries logs via NerdGraph GraphQL API
   - Implements timestamp-based "tailing" via polling
   - Extracts latest timestamp from results for next query
   - Handles both millisecond and second timestamps

2. **log_processor.py** - Log filtering and data extraction
   - Filters logs based on regex patterns and required fields
   - Extracts data using field mapping (supports nested fields)
   - Optional regex-based extraction from log messages
   - Preserves original log for debugging

3. **graphql_client.py** - GraphQL mutation client
   - Executes mutations against local backend
   - Batch processing support
   - Maps extracted log data to mutation variables
   - Error handling and reporting

4. **log_tailer.py** - Main orchestration
   - Polls New Relic at configured interval
   - Coordinates fetching, filtering, and sending
   - Tracks statistics (sent, errors)
   - Configurable via JSON file
   - Command-line interface

5. **test_server.py** - Test GraphQL server
   - Simple HTTP server for local testing
   - Receives and logs mutations
   - Returns success responses
   - Useful for development without real backend

### Key Design Decisions

- **Polling vs Streaming**: Used polling approach since New Relic doesn't offer true streaming API
- **Timestamp Tracking**: Maintains last seen timestamp to avoid reprocessing logs
- **Modular Design**: Separated concerns (API client, processing, GraphQL) for reusability
- **Configuration-Driven**: All behavior configurable via JSON (NRQL query, filters, mappings)
- **Error Handling**: Graceful handling of API errors, network issues, and malformed data

### Challenges & Solutions

1. **Challenge**: New Relic doesn't have streaming API
   - **Solution**: Implement polling with timestamp tracking

2. **Challenge**: Different timestamp formats in logs
   - **Solution**: Auto-detect and handle both second/millisecond timestamps

3. **Challenge**: Flexible field mapping
   - **Solution**: Dot-notation path syntax for nested fields

4. **Challenge**: Testing without production backend
   - **Solution**: Built simple test GraphQL server

### Testing Approach

- Created test server for local development
- Configurable poll intervals for testing vs production
- Verbose mode for debugging
- Statistics tracking for monitoring

### Files Created

- `newrelic_client.py` - New Relic API client
- `log_processor.py` - Log filtering and extraction
- `graphql_client.py` - GraphQL mutation client
- `log_tailer.py` - Main CLI application
- `test_server.py` - Test GraphQL server
- `config.example.json` - Basic configuration template
- `config.advanced.example.json` - Advanced features demo
- `.env.example` - Environment variable template
- `requirements.txt` - Python dependencies
- `USAGE.md` - Comprehensive usage guide
- `README.md` - Complete project documentation
- `.gitignore` - Git ignore patterns

**Total**: ~686 lines of Python code

## Summary

Successfully built a complete POC that:
1. ✅ Polls New Relic logs via NerdGraph API
2. ✅ Filters logs based on configurable criteria
3. ✅ Extracts data from log messages and metadata
4. ✅ Maps extracted data to GraphQL mutation variables
5. ✅ Executes mutations against local backend
6. ✅ Includes test server for development
7. ✅ Fully configurable via JSON
8. ✅ CLI interface with options
9. ✅ Comprehensive documentation

The POC is production-ready for testing purposes and demonstrates a complete
solution for replaying production logs as GraphQL mutations against a local
backend.
