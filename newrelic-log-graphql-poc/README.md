# New Relic Log to GraphQL POC

A proof-of-concept tool that tails log streams from New Relic, filters and extracts data from log messages, and replays them as GraphQL mutations against a local backend. This enables testing local endpoints with real production request patterns.

## Overview

This POC demonstrates how to:
1. **Tail logs** from New Relic using the NerdGraph API
2. **Filter** specific log messages based on patterns and criteria
3. **Extract** relevant data from log messages and metadata
4. **Map** extracted data to GraphQL mutation variables
5. **Execute** mutations against a local backend for testing

## Use Cases

- **Local Testing**: Test local API endpoints with real production traffic patterns
- **Error Replay**: Replay production errors locally for debugging
- **Load Testing**: Generate realistic request patterns from production logs
- **Integration Testing**: Validate changes against actual production data
- **Debugging**: Reproduce production issues in local environment

## Architecture

```
┌─────────────────┐
│   New Relic     │
│   (NerdGraph)   │
└────────┬────────┘
         │ Poll logs via NRQL
         │ (timestamp-based)
         ▼
┌─────────────────┐
│  Log Processor  │
│  - Filter logs  │
│  - Extract data │
└────────┬────────┘
         │ Processed data
         ▼
┌─────────────────┐
│ GraphQL Client  │
│  - Map to vars  │
│  - Execute mut. │
└────────┬────────┘
         │ Mutations
         ▼
┌─────────────────┐
│ Local Backend   │
│  (GraphQL API)  │
└─────────────────┘
```

## Components

### Core Modules

- **`newrelic_client.py`**: NerdGraph API client for querying logs
- **`log_processor.py`**: Log filtering and data extraction engine
- **`graphql_client.py`**: GraphQL mutation execution client
- **`log_tailer.py`**: Main orchestrator with CLI interface

### Supporting Files

- **`test_server.py`**: Simple GraphQL server for testing
- **`config.example.json`**: Basic configuration template
- **`config.advanced.example.json`**: Advanced configuration examples
- **`requirements.txt`**: Python dependencies
- **`USAGE.md`**: Detailed usage guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config.example.json config.json
# Edit config.json with your New Relic credentials and settings
```

Required configuration:
- **New Relic API Key**: User API key (get from New Relic One → API Keys)
- **Account ID**: Your New Relic account ID
- **NRQL Query**: Query to fetch logs (e.g., `SELECT * FROM Log WHERE service.name = 'api'`)
- **GraphQL Endpoint**: Your local backend URL
- **Mutation Template**: GraphQL mutation to execute

### 3. Run

**Option A: With test server**

```bash
# Terminal 1: Start test server
python test_server.py

# Terminal 2: Run log tailer
python log_tailer.py -c config.json -v
```

**Option B: Against your local backend**

```bash
python log_tailer.py -c config.json
```

## Configuration

### Basic Configuration

```json
{
  "newrelic": {
    "api_key": "NRAK-YOUR-API-KEY",
    "account_id": "1234567",
    "nrql_query": "SELECT * FROM Log WHERE service.name = 'my-service'",
    "poll_interval_seconds": 5
  },
  "graphql": {
    "endpoint": "http://localhost:4000/graphql",
    "mutation_template": "mutation CreateEvent($data: EventInput!) { createEvent(data: $data) { id success } }"
  },
  "filters": {
    "message_pattern": ".*",
    "required_fields": ["message", "timestamp"]
  },
  "mapping": {
    "message": "message",
    "timestamp": "timestamp",
    "level": "level",
    "service": "service.name"
  }
}
```

### Field Mapping

The `mapping` section defines how to extract data from New Relic logs:

```json
"mapping": {
  "targetField": "sourceField",        // Direct mapping
  "userId": "user.id",                 // Nested field access
  "service": "service.name"            // Dot notation
}
```

### Filtering

Filter logs before processing:

```json
"filters": {
  "message_pattern": "^ERROR.*",       // Regex for message content
  "required_fields": ["message", "timestamp", "user_id"]
}
```

## Command-Line Options

```bash
python log_tailer.py [OPTIONS]

Options:
  -c, --config PATH       Configuration file path (default: config.json)
  -n, --iterations N      Number of polling iterations (default: infinite)
  -v, --verbose          Enable verbose output
```

## Examples

### Example 1: Replay Error Logs

```json
{
  "newrelic": {
    "nrql_query": "SELECT * FROM Log WHERE level = 'ERROR' AND service.name = 'api-gateway'"
  },
  "filters": {
    "message_pattern": "^ERROR.*"
  }
}
```

### Example 2: Test Specific Endpoints

```json
{
  "newrelic": {
    "nrql_query": "SELECT * FROM Log WHERE message LIKE '%POST /api/orders%'"
  },
  "graphql": {
    "mutation_template": "mutation TestOrder($data: OrderInput!) { createOrder(data: $data) { id } }"
  }
}
```

### Example 3: User Activity Replay

```json
{
  "newrelic": {
    "nrql_query": "SELECT * FROM Log WHERE user_id IS NOT NULL"
  },
  "filters": {
    "required_fields": ["user_id", "action", "timestamp"]
  },
  "mapping": {
    "userId": "user_id",
    "action": "action",
    "timestamp": "timestamp"
  }
}
```

## How It Works

### 1. Polling Mechanism

The tool polls New Relic at regular intervals (configurable via `poll_interval_seconds`). It uses timestamp tracking to fetch only new logs since the last query:

```
First query:  "SELECT ... SINCE 1 minute ago"
Next queries: "SELECT ... SINCE {last_timestamp}"
```

### 2. Filtering

Logs are filtered based on:
- **Message pattern**: Regex match on log message
- **Required fields**: Ensures specific fields exist
- **Custom logic**: Extensible via `LogProcessor` class

### 3. Data Extraction

Data is extracted using:
- **Field mapping**: Direct or nested field access (dot notation)
- **Regex extraction**: Pattern-based extraction from message text
- **Original preservation**: Full log kept for debugging (`_original_log`)

### 4. GraphQL Execution

Extracted data is:
1. Mapped to mutation variables
2. Wrapped in expected input structure
3. Sent as GraphQL mutation
4. Response tracked for success/failure

## Features

- ✅ **Timestamp-based tailing**: Only fetch new logs
- ✅ **Flexible filtering**: Regex patterns and field requirements
- ✅ **Nested field mapping**: Access deep object properties
- ✅ **Batch processing**: Process multiple logs efficiently
- ✅ **Error handling**: Graceful handling of API/network errors
- ✅ **Statistics tracking**: Monitor sent/failed mutations
- ✅ **Verbose mode**: Detailed logging for debugging
- ✅ **Test server**: Built-in mock GraphQL server
- ✅ **Configuration-driven**: No code changes needed

## Limitations

- **Polling, not streaming**: Uses polling with configurable interval (New Relic doesn't offer true log streaming API)
- **Rate limits**: Subject to New Relic API rate limits
- **Timestamp precision**: Relies on log timestamps; may miss logs with same timestamp
- **Sequential processing**: Processes logs one at a time (could be parallelized)

## Future Enhancements

Potential improvements for production use:

1. **Parallel Processing**: Process and send mutations concurrently
2. **State Persistence**: Save last timestamp to disk for restarts
3. **Retry Logic**: Exponential backoff for failed mutations
4. **Metrics/Monitoring**: Export metrics (Prometheus, StatsD)
5. **Batched Mutations**: Send multiple mutations in single request
6. **Authentication**: Support for auth headers/tokens
7. **Dead Letter Queue**: Store failed mutations for replay
8. **Docker Support**: Containerize for easy deployment
9. **Multiple Backends**: Support sending to multiple endpoints
10. **Transformation Pipeline**: Plugin system for custom transformations

## Technical Details

### Dependencies

- `requests`: HTTP client for API calls
- `python-dotenv`: Environment variable management
- `gql`: GraphQL client library
- `requests-toolbelt`: Additional HTTP utilities

### API Used

- **New Relic NerdGraph**: `https://api.newrelic.com/graphql`
- **Authentication**: API-Key header with User API key
- **Query Language**: NRQL (New Relic Query Language)

### Timestamp Handling

The tool automatically handles different timestamp formats:
- Millisecond timestamps (JavaScript style)
- Second timestamps (Unix style)
- Auto-detection and normalization

## Troubleshooting

### No logs appearing
- Verify NRQL query in New Relic UI
- Check API key permissions (must be User key)
- Confirm account ID is correct
- Test with longer time window (e.g., `SINCE 1 hour ago`)

### GraphQL mutations failing
- Verify endpoint is accessible
- Check mutation template syntax
- Validate field mappings
- Enable verbose mode: `python log_tailer.py -v`

### Rate limiting
- Increase `poll_interval_seconds`
- Reduce query time window
- Check New Relic API limits for your account

## Development

### Running Tests

```bash
# Start test server
python test_server.py

# In another terminal, run with test config
python log_tailer.py -c config.example.json -n 5 -v
```

### Adding Custom Filters

Extend `LogProcessor` class in `log_processor.py`:

```python
def custom_filter(self, log: Dict[str, Any]) -> bool:
    # Your custom logic
    return True
```

### Custom Data Extraction

Use regex patterns in config:

```json
"extraction": {
  "patterns": {
    "user_id": "user_id=([0-9]+)",
    "request_id": "request_id=([a-f0-9-]+)"
  }
}
```

## License

MIT License - This is a proof of concept for demonstration purposes.

## Author

Built as a POC for testing local backends with production log data.

## Contributing

This is a proof of concept. For production use, consider the enhancements listed above.

---

**Note**: This tool is designed for development and testing purposes. Always ensure you have proper authorization before accessing production logs and be mindful of sensitive data in log messages.
