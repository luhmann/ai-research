# New Relic Log to GraphQL Mutation POC

A proof-of-concept tool that tails New Relic logs, filters them based on configurable rules, extracts data, and replays them as GraphQL mutations against a local backend. This is useful for testing local endpoints with real production log data.

## Overview

This POC demonstrates how to:

1. **Poll New Relic logs** using the NerdGraph API (GraphQL)
2. **Filter logs** based on flexible matching rules
3. **Extract data** from log messages and metadata
4. **Map log data** to GraphQL mutation variables
5. **Execute mutations** against a local GraphQL backend

## Architecture

```
┌─────────────────┐
│  New Relic      │
│  (NerdGraph)    │
└────────┬────────┘
         │ Poll with NRQL
         │ (timestamp-based queries)
         ▼
┌─────────────────┐
│  Log Poller     │
│  - Query logs   │
│  - Track offset │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Filter Engine  │
│  - Match rules  │
│  - Extract data │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GraphQL Mapper │
│  - Map fields   │
│  - Transform    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Local GraphQL  │
│  Backend        │
└─────────────────┘
```

## Features

- **Flexible Filtering**: Support for multiple operators (equals, contains, regex, exists, gt, lt)
- **Nested Field Access**: Access nested fields like `attributes.userId`
- **Data Transformation**: Built-in transforms (lowercase, uppercase, trim, parseInt, parseFloat, json)
- **Multiple Mappings**: Define multiple log-to-mutation mappings
- **Configurable Polling**: Adjust polling interval to suit your needs
- **Dual Configuration**: Use JSON config file or environment variables
- **Error Handling**: Graceful error handling with detailed logging

## Installation

```bash
# Install dependencies (already done if generated via init)
bun install
```

## Configuration

### Option 1: Configuration File (Recommended)

Create a `config.json` file:

```bash
bun run init config.json
```

This creates a sample configuration. Edit it with your settings:

```json
{
  "newRelic": {
    "apiKey": "YOUR_NEW_RELIC_USER_API_KEY",
    "accountId": "YOUR_ACCOUNT_ID",
    "pollingIntervalMs": 10000
  },
  "backend": {
    "endpoint": "http://localhost:4000/graphql",
    "headers": {
      "Authorization": "Bearer YOUR_TOKEN"
    }
  },
  "nrqlQuery": "SELECT * FROM Log WHERE service = 'my-service'",
  "mappings": [
    {
      "name": "user-signup-event",
      "filters": [
        {
          "field": "message",
          "operator": "contains",
          "value": "User signed up"
        },
        {
          "field": "attributes.userId",
          "operator": "exists"
        }
      ],
      "mutation": "mutation CreateUser($userId: ID!, $email: String!) { ... }",
      "extractors": [
        {
          "sourcePath": "attributes.userId",
          "targetField": "userId"
        },
        {
          "sourcePath": "attributes.email",
          "targetField": "email",
          "transform": "lowercase"
        }
      ]
    }
  ]
}
```

### Option 2: Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:

```env
NEW_RELIC_API_KEY=YOUR_API_KEY
NEW_RELIC_ACCOUNT_ID=YOUR_ACCOUNT_ID
GRAPHQL_ENDPOINT=http://localhost:4000/graphql
POLLING_INTERVAL_MS=10000
```

**Note**: When using environment variables, you'll need to provide mappings programmatically or via config file.

## Usage

### Start Log Tailing (Continuous)

With config file:
```bash
bun run start --config config.json
```

With environment variables:
```bash
bun run start
```

### Run Once (Testing)

Useful for testing your configuration:

```bash
bun run once --config config.json
```

This will fetch logs once and exit, helping you verify your filters and mappings.

### Development Mode (Auto-reload)

```bash
bun run dev --config config.json
```

## Configuration Details

### Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `equals` | Exact match | `{"field": "status", "operator": "equals", "value": "success"}` |
| `contains` | String/array contains | `{"field": "message", "operator": "contains", "value": "error"}` |
| `regex` | Regex pattern match | `{"field": "message", "operator": "regex", "value": "Order.*placed"}` |
| `exists` | Field exists | `{"field": "attributes.userId", "operator": "exists"}` |
| `gt` | Greater than (numbers) | `{"field": "duration", "operator": "gt", "value": 1000}` |
| `lt` | Less than (numbers) | `{"field": "duration", "operator": "lt", "value": 100}` |

### Data Transformations

| Transform | Description | Example |
|-----------|-------------|---------|
| `lowercase` | Convert to lowercase | `"USER@EMAIL.COM"` → `"user@email.com"` |
| `uppercase` | Convert to uppercase | `"hello"` → `"HELLO"` |
| `trim` | Trim whitespace | `" hello "` → `"hello"` |
| `parseInt` | Parse integer | `"42"` → `42` |
| `parseFloat` | Parse float | `"3.14"` → `3.14` |
| `json` | Parse JSON string | `'{"foo":"bar"}'` → `{foo: "bar"}` |

### Mapping Structure

Each mapping consists of:

1. **name**: Identifier for the mapping
2. **filters**: Array of filter rules (ALL must match)
3. **mutation**: GraphQL mutation string
4. **extractors**: Array of extraction rules

Example:

```json
{
  "name": "order-placed",
  "filters": [
    {
      "field": "message",
      "operator": "contains",
      "value": "Order placed"
    },
    {
      "field": "attributes.orderId",
      "operator": "exists"
    }
  ],
  "mutation": "mutation CreateOrder($orderId: ID!, $total: Float!) { createOrder(orderId: $orderId, total: $total) { id } }",
  "extractors": [
    {
      "sourcePath": "attributes.orderId",
      "targetField": "orderId"
    },
    {
      "sourcePath": "attributes.total",
      "targetField": "total",
      "transform": "parseFloat",
      "defaultValue": 0.0
    }
  ]
}
```

## Getting New Relic Credentials

1. **API Key**: Go to [New Relic API Keys](https://one.newrelic.com/api-keys) and create a User API key
2. **Account ID**: Find it in the URL when logged into New Relic: `https://one.newrelic.com/account/<ACCOUNT_ID>/...`

## Example Use Cases

### 1. Testing User Signup Flow

Monitor production logs for user signup events and replay them against your local backend:

```json
{
  "name": "user-signup",
  "filters": [
    {"field": "message", "operator": "contains", "value": "signup"},
    {"field": "attributes.email", "operator": "exists"}
  ],
  "mutation": "mutation CreateUser($email: String!, $name: String) { ... }",
  "extractors": [
    {"sourcePath": "attributes.email", "targetField": "email"},
    {"sourcePath": "attributes.name", "targetField": "name"}
  ]
}
```

### 2. Testing Payment Processing

Capture payment events from production logs:

```json
{
  "name": "payment-processed",
  "filters": [
    {"field": "message", "operator": "regex", "value": "Payment.*processed"},
    {"field": "attributes.amount", "operator": "gt", "value": 0}
  ],
  "mutation": "mutation ProcessPayment($amount: Float!, $userId: ID!) { ... }",
  "extractors": [
    {"sourcePath": "attributes.amount", "targetField": "amount", "transform": "parseFloat"},
    {"sourcePath": "attributes.userId", "targetField": "userId"}
  ]
}
```

## Technical Details

### Log Polling Approach

Since New Relic doesn't provide a true streaming API, this POC uses a polling approach:

1. Query logs with `WHERE timestamp > lastSeenTimestamp`
2. Process returned logs
3. Update `lastSeenTimestamp` to the most recent log
4. Wait for polling interval
5. Repeat

This effectively simulates "tailing" the log stream.

### NerdGraph Query Structure

The POC uses New Relic's NerdGraph GraphQL API:

```graphql
query($accountId: Int!, $nrql: Nrql!) {
  actor {
    account(id: $accountId) {
      nrql(query: $nrql) {
        results
      }
    }
  }
}
```

NRQL queries look like: `SELECT * FROM Log WHERE timestamp > 1234567890 ORDER BY timestamp ASC LIMIT 1000`

## Limitations

1. **Not True Streaming**: Uses polling, so there's a delay based on polling interval
2. **Query Limits**: New Relic limits query results (1000 logs per query in this POC)
3. **Timestamp Precision**: May miss logs with identical timestamps
4. **No State Persistence**: Timestamp tracking is in-memory only (resets on restart)

## Future Enhancements

- Add retry logic for failed mutations
- Implement rate limiting
- Add metrics and monitoring
- Support batch mutations (reduce API calls)
- Persist timestamp state to disk
- Add support for webhook delivery option
- Support for multiple New Relic accounts
- Add filtering by log level/severity

## Troubleshooting

### No logs appearing

1. Check your NRQL query is correct
2. Verify API key has read permissions
3. Ensure account ID is correct
4. Check if logs exist in the time window (starts from 5 minutes ago)

### GraphQL mutations failing

1. Verify your backend is running
2. Check the mutation syntax is correct
3. Ensure extracted fields match mutation variables
4. Review error logs for detailed error messages

### Duplicate logs

If you see duplicate logs being processed:
- This shouldn't happen with the timestamp tracking, but if it does, check your polling interval isn't too aggressive

## License

This is a proof-of-concept for educational and testing purposes.

## Contributing

This is a POC. Feel free to extend and adapt for your use case!
