# New Relic Log to GraphQL POC - Development Notes

## Goal
Create a POC that tails New Relic logs, filters messages, extracts data, and replays them as GraphQL mutations against a local backend.

## Research Phase

### New Relic Log Streaming Options

1. **Live Tail Feature**: New Relic has a UI-based live tail feature but this is browser-based
2. **Log API**: Primarily for *sending* logs to New Relic (https://log-api.newrelic.com/log/v1)
3. **NerdGraph API**: Need to investigate if this supports querying/streaming logs programmatically

### NerdGraph API Findings

**Key Discoveries:**
- NerdGraph is New Relic's GraphQL API
- Supports NRQL (New Relic Query Language) for querying logs
- Uses API key authentication (User API Key)
- Supports both sync and async queries
- Can query logs with: `SELECT * FROM Log WHERE ...`

**Authentication:**
- Requires New Relic User API Key
- Passed in header: `Api-Key: YOUR_KEY`
- Endpoint: `https://api.newrelic.com/graphql`

**Approach for "Tailing":**
Since NerdGraph doesn't provide true streaming, we'll implement:
1. Polling approach with timestamp-based queries
2. Query logs with `WHERE timestamp > lastSeenTimestamp`
3. Track last seen timestamp to avoid duplicates
4. Configurable polling interval

### Architecture Design

```
┌─────────────────┐
│  New Relic      │
│  (NerdGraph)    │
└────────┬────────┘
         │ Poll with NRQL
         │ (SINCE X minutes ago)
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
│  - Map to       │
│    mutation     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Local GraphQL  │
│  Backend        │
└─────────────────┘
```

### Implementation Details

**Core Components Built:**

1. **NewRelicClient** (`src/newrelic-client.ts`)
   - Polls New Relic NerdGraph API using NRQL queries
   - Tracks last seen timestamp to avoid duplicates
   - Supports configurable polling intervals
   - Query structure: `SELECT * FROM Log WHERE timestamp > X`

2. **FilterEngine** (`src/filter-engine.ts`)
   - Supports multiple filter operators: equals, contains, regex, exists, gt, lt
   - Nested field access (e.g., `attributes.userId`)
   - Data extraction with transformations
   - Transformations: lowercase, uppercase, trim, parseInt, parseFloat, json

3. **BackendGraphQLClient** (`src/graphql-client.ts`)
   - Executes GraphQL mutations against local backend
   - Parallel mutation execution
   - Error handling and logging

4. **LogReplayOrchestrator** (`src/orchestrator.ts`)
   - Coordinates all components
   - Processes logs in batches
   - Supports continuous polling or one-time execution

5. **ConfigLoader** (`src/config-loader.ts`)
   - Loads config from JSON file or environment variables
   - Validates configuration
   - Can generate sample config

**Configuration System:**

Two options:
1. JSON config file with `--config` flag
2. Environment variables (see `.env.example`)

**Mapping Configuration:**
- Each mapping has filters (all must match)
- Extractors define how to map log fields to GraphQL variables
- Supports default values and transformations

### Challenges and Learnings

1. **No True Streaming**: New Relic doesn't provide a true streaming API. Implemented polling with timestamp-based queries to simulate tailing.

2. **Timestamp Tracking**: Need to track the last seen timestamp to avoid processing duplicate logs between polls.

3. **GraphQL Query Structure**: NerdGraph uses a specific structure with `actor.account.nrql.results` for querying logs.

4. **Flexible Filtering**: Built a flexible filter engine that supports various operators and nested field access.

### Next Steps for Production Use

- Add retry logic for failed mutations
- Implement rate limiting
- Add metrics and monitoring
- Support for batch mutations (reduce API calls)
- Add support for query templates
- Implement stateful timestamp persistence (survive restarts)
