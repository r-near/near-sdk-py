# NEAR SDK Python Collections Performance Analysis

## Overview

This document summarizes the performance characteristics of various collection types in the NEAR SDK Python. All tests were performed with collections containing 10,000 elements. Performance is measured in TGas (Tera Gas units, or 10^12 gas units), which represents the computational cost on the NEAR blockchain.

## Executive Summary

- **Lookup-based collections** (LookupMap, LookupSet) offer the most efficient access and basic operations, with most operations using approximately the same gas as a simple function call (1.00x baseline).
- **Ordered collections** (Vector, UnorderedMap, UnorderedSet) have slightly higher overhead for basic operations but offer additional functionality like iteration and pagination.
- **Common operations** (contains/get) are highly optimized across all collection types, typically only 1.00-1.07x the baseline.
- **Mutating operations** (adding, removing) are more expensive, with the most complex operations (remove in UnorderedSet) costing up to 1.62x the baseline.

## Detailed Results by Collection Type

### 1. LookupMap Performance

LookupMap provides key-value storage with O(1) lookup time.

| Operation | Gas (TGas) | vs. Baseline | Comment |
|-----------|------------|--------------|---------|
| contains_key (existing) | 6.8921 | 1.00x | Virtually no overhead |
| contains_key (non-existing) | 6.9277 | 1.00x | Similar cost to contains |
| get | 6.9733 | 1.01x | Extremely efficient retrieval |
| set (update existing) | 7.2679 | 1.05x | Low overhead for updates |
| set (add new) | 7.7680 | 1.13x | Slightly more expensive than updates |
| remove | 7.9393 | 1.15x | Most expensive operation but still reasonable |

**Best for**: Simple key-value storage when iteration is not needed.

### 2. LookupSet Performance

LookupSet provides unique value storage with O(1) membership tests.

| Operation | Gas (TGas) | vs. Baseline | Comment |
|-----------|------------|--------------|---------|
| contains (existing) | 6.9288 | 1.00x | Virtually no overhead |
| contains (non-existing) | 6.9601 | 1.00x | Similar cost to contains |
| add (new value) | 7.7404 | 1.11x | Moderate cost for new additions |
| add (existing value) | 6.9185 | 1.00x | No-op when value exists |
| remove | 7.9045 | 1.14x | Similar to LookupMap removal |
| discard (existing) | 7.9006 | 1.14x | Similar to remove but doesn't throw if missing |
| discard (non-existing) | 6.9697 | 1.00x | No-op when value doesn't exist |

**Best for**: Checking membership in a set when iteration is not needed.

### 3. UnorderedMap Performance

UnorderedMap provides key-value storage with O(1) lookup time and supports iteration.

| Operation | Gas (TGas) | vs. Baseline | Comment |
|-----------|------------|--------------|---------|
| get_length | 7.6414 | 1.03x | Efficient length check |
| get_item (key lookup) | 7.6056 | 1.03x | Slightly more overhead than LookupMap |
| contains_key | ~7.60 | 1.03x | Similar cost to retrieval |
| remove_item | 11.9519 | 1.62x | Highest relative cost due to additional index maintenance |
| set_item (insert new) | 9.8328 | 1.33x | More expensive than LookupMap due to tracking for iteration |
| get_paginated_items | 10.2286 | 1.38x | Additional cost for pagination support |

**Best for**: Key-value storage when iteration or pagination is needed.

### 4. Vector Performance

Vector provides ordered, indexed storage with O(1) access by index.

| Operation | Gas (TGas) | vs. Baseline | Comment |
|-----------|------------|--------------|---------|
| get_length | 6.9997 | 1.04x | Efficient length check |
| get_item (random access) | 7.2269 | 1.07x | Consistent access time regardless of position |
| pop_item | 7.8561 | 1.16x | Efficient removal from the end |
| swap_remove_item | 8.3108 | 1.23x | More expensive due to swap operation |
| add_item | 8.0219 | 1.19x | Moderate cost for appending |

**Best for**: Ordered data where index-based access is important.

## Performance Optimization Recommendations

1. **Choose the appropriate collection type** for your specific use case:
   - Use LookupMap/LookupSet when you only need to check existence or retrieve values.
   - Use UnorderedMap/UnorderedSet when you need iteration capabilities.
   - Use Vector when order matters or when you need index-based access.

2. **Optimize for gas efficiency**:
   - Avoid unnecessary additions and removals, especially with UnorderedMap/UnorderedSet.
   - Consider batch operations where possible.
   - Use contains/exists checks before operations to avoid unnecessary gas usage.

3. **Consider implementation details**:
   - The optimized UnorderedMap/UnorderedSet implementations use indices to make removals more efficient (O(1) instead of O(n)).
   - Vectors provide the most consistent performance across different positions in the collection.

## Testing Methodology

All tests were conducted on a NEAR sandbox environment using near-pytest with systematically patched state to create collections with 10,000 elements. Operations were measured using the receipt_outcome gas_burnt metrics and normalized against a simple "hello world" function call as the baseline.

Tests were run on March 20, 2025, with consistent hardware and environment settings for all collection types.