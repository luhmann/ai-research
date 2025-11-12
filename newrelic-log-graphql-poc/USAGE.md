# Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure the Application

Copy the example configuration:

```bash
cp config.example.json config.json
```

Edit `config.json` with your settings:

```json
{
  "newrelic": {
    "api_key": "YOUR_NEW_RELIC_USER_API_KEY",
    "account_id": "1234567",
    "nrql_query": "SELECT * FROM Log WHERE service.name = 'my-service'",
    "poll_interval_seconds": 5
  },
  "graphql": {
    "endpoint": "http://localhost:4000/graphql",
    "mutation_template": "mutation CreateEvent($data: EventInput!) { createEvent(data: $data) { id success } }"
  }
}
```

### 3. Start the Test Server (Optional)

For testing, start the included test GraphQL server:

```bash
python test_server.py
```

This will start a simple GraphQL server on `http://localhost:4000/graphql` that receives and logs mutations.

### 4. Run the Log Tailer

```bash
python log_tailer.py -c config.json -v
```

Options:
- `-c, --config`: Path to configuration file (default: config.json)
- `-n, --iterations`: Number of polling iterations (default: infinite)
- `-v, --verbose`: Enable verbose output

## Configuration Reference

### New Relic Settings

```json
"newrelic": {
  "api_key": "NRAK-...",           // Your New Relic User API Key
  "account_id": "1234567",          // Your New Relic Account ID
  "nrql_query": "SELECT ...",       // NRQL query (without SINCE clause)
  "poll_interval_seconds": 5        // How often to poll for new logs
}
```

**Getting Your API Key:**
1. Go to New Relic One
2. Click on your user menu → API Keys
3. Create a USER key (not INGEST or LICENSE key)

**Finding Your Account ID:**
1. Go to New Relic One
2. Look at the URL: `https://one.newrelic.com/accounts/YOUR_ACCOUNT_ID/...`

### GraphQL Settings

```json
"graphql": {
  "endpoint": "http://localhost:4000/graphql",
  "mutation_template": "mutation CreateEvent($data: EventInput!) { ... }"
}
```

The mutation template should:
- Accept a `$data` variable
- Match your backend's schema

### Filters

```json
"filters": {
  "message_pattern": "^ERROR.*",      // Regex pattern for log messages
  "required_fields": ["message"]      // Fields that must be present
}
```

### Mapping

Map New Relic log fields to GraphQL mutation variables:

```json
"mapping": {
  "message": "message",               // Direct field mapping
  "timestamp": "timestamp",
  "userId": "user.id",                // Nested field access
  "service": "service.name"
}
```

## Advanced Usage

### Custom Data Extraction

For extracting data from log messages using regex, see `config.advanced.example.json`.

### Filtering Specific Log Types

```json
"nrql_query": "SELECT * FROM Log WHERE service.name = 'api' AND level IN ('ERROR', 'FATAL')"
```

### Multiple Services

Create separate config files for different services:

```bash
python log_tailer.py -c config.api.json &
python log_tailer.py -c config.worker.json &
```

## Troubleshooting

### No logs appearing

1. Check your NRQL query in New Relic UI first
2. Verify your API key has correct permissions
3. Check account ID is correct
4. Increase poll interval if hitting rate limits

### GraphQL mutations failing

1. Check the GraphQL endpoint is accessible
2. Verify mutation template matches your schema
3. Check field mappings are correct
4. Enable verbose mode to see full data

### Authentication errors

- Make sure you're using a USER API key, not an INGEST or LICENSE key
- Verify the key hasn't expired

## Examples

### Example 1: Error Log Replay

Replay all error logs from production to test error handling locally:

```json
{
  "newrelic": {
    "nrql_query": "SELECT * FROM Log WHERE level = 'error' AND service.name = 'production-api'"
  },
  "graphql": {
    "mutation_template": "mutation TestError($data: ErrorInput!) { testError(data: $data) { handled } }"
  }
}
```

### Example 2: Request Replay

Replay specific API requests:

```json
{
  "newrelic": {
    "nrql_query": "SELECT * FROM Log WHERE message LIKE '%POST /api/orders%'"
  },
  "filters": {
    "message_pattern": "POST /api/orders.*"
  },
  "graphql": {
    "mutation_template": "mutation ReplayOrder($data: OrderInput!) { createOrder(data: $data) { id } }"
  }
}
```
