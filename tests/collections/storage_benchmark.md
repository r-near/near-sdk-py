# NEAR SDK Collections Storage Benchmark Results

## Testing Methodology

These benchmarks measure storage usage in a simulated environment rather than on the actual NEAR blockchain. We use the mock storage implementation from the test fixtures (`setup_storage_mocks`) that simulates blockchain storage with an in-memory dictionary. The storage size is calculated by measuring the total size of keys and values in this dictionary.

While this approach doesn't capture all aspects of on-chain execution (such as gas metering, validator processing, etc.), it provides an accurate representation of the storage patterns and relative efficiency of different collection types. The storage measurements here should correlate directly with gas costs when deployed on the NEAR blockchain, as gas pricing is heavily influenced by storage usage.

## Vector Storage Usage

| Operation | Items | Initial Size (bytes) | Final Size (bytes) | Difference (bytes) | Bytes per Item |
|-----------|-------|----------------------|--------------------|-------------------|---------------|
| Creation | 0 | 0 | 72 | 72 | N/A |
| Append 10 small strings | 10 | 0 | 402 | 402 | 40.20 |
| Append 100 small strings | 100 | 0 | 3552 | 3552 | 35.52 |
| Append 1000 small strings | 1000 | 0 | 36853 | 36853 | 36.85 |
| Append 10000 small strings | 10000 | 0 | 387853 | 387853 | 38.79 |
| Append 10 large strings (1KB) | 10 | 0 | 10382 | 10382 | 1038.20 |
| Append 100 large strings (1KB) | 100 | 0 | 103262 | 103262 | 1032.62 |
| Append 1000 large strings (1KB) | 1000 | 0 | 1032963 | 1032963 | 1032.96 |

## LookupMap Storage Usage

| Operation | Items | Initial Size (bytes) | Final Size (bytes) | Difference (bytes) | Bytes per Item |
|-----------|-------|----------------------|--------------------|-------------------|---------------|
| Creation | 0 | 0 | 69 | 69 | N/A |
| Set 10 small key-values | 10 | 0 | 409 | 409 | 40.90 |
| Set 100 small key-values | 100 | 0 | 3649 | 3649 | 36.49 |
| Set 1000 small key-values | 1000 | 0 | 37850 | 37850 | 37.85 |
| Set 10000 small key-values | 10000 | 0 | 397850 | 397850 | 39.78 |

## LookupSet Storage Usage

| Operation | Items | Initial Size (bytes) | Final Size (bytes) | Difference (bytes) | Bytes per Item |
|-----------|-------|----------------------|--------------------|-------------------|---------------|
| Creation | 0 | 0 | 69 | 69 | N/A |
| Add 10 items | 10 | 0 | 249 | 249 | 24.90 |
| Add 100 items | 100 | 0 | 1959 | 1959 | 19.59 |
| Add 1000 items | 1000 | 0 | 19960 | 19960 | 19.96 |
| Add 10000 items | 10000 | 0 | 208960 | 208960 | 20.90 |

## UnorderedMap Storage Usage

| Operation | Items | Initial Size (bytes) | Final Size (bytes) | Difference (bytes) | Bytes per Item |
|-----------|-------|----------------------|--------------------|-------------------|---------------|
| Creation | 0 | 0 | 143 | 143 | N/A |
| Set 10 small key-values | 10 | 0 | 823 | 823 | 82.30 |
| Set 100 small key-values | 100 | 0 | 7303 | 7303 | 73.03 |
| Set 1000 small key-values | 1000 | 0 | 75705 | 75705 | 75.70 |
| Set 10000 small key-values | 10000 | 0 | 795705 | 795705 | 79.57 |

## TreeMap Storage Usage

| Operation | Items | Initial Size (bytes) | Final Size (bytes) | Difference (bytes) | Bytes per Item |
|-----------|-------|----------------------|--------------------|-------------------|---------------|
| Creation | 0 | 0 | 143 | 143 | N/A |
| Set 10 items | 10 | 0 | 653 | 653 | 65.30 |
| Set 100 items | 100 | 0 | 5513 | 5513 | 55.13 |
| Set 1000 items | 1000 | 0 | 64255 | 64255 | 64.25 |
| Set 10000 items | 10000 | 0 | 694255 | 694255 | 69.43 |

## Summary of Storage Efficiency

| Collection Type | Initialization Cost (bytes) | Storage per Item (bytes) | Notes |
|-----------------|-----------------------------|-----------------------------|-------|
| LookupSet | 69 | ~20 | Most efficient for membership testing |
| Vector | 72 | ~36-39 | Efficient for sequential access |
| LookupMap | 69 | ~37-40 | Good for key-value without iteration |
| TreeMap | 143 | ~55-70 | Provides ordering capabilities |
| UnorderedMap | 143 | ~73-80 | Least efficient, but allows iteration |