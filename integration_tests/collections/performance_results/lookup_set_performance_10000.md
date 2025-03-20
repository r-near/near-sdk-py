# LookupSet Performance Test Results

LookupSet size: 10000 elements

| Operation | Gas (TGas) | vs. Baseline | Details |
|-----------|------------|--------------|----------|
| hello world (baseline) | 6.9463 | 1.00x | Basic function call |
| contains (existing) | 6.9288 | 1.00x | Average of 6 values |
| contains (non-existing) | 6.9601 | 1.00x | Check for a value that doesn't exist |
| add (new value) | 7.7404 | 1.11x | Add a new value to the set |
| add (existing value) | 6.9185 | 1.00x | Add a value that already exists (no-op) |
| remove | 7.9045 | 1.14x | Remove an existing value |
| discard (existing) | 7.9006 | 1.14x | Discard an existing value |
| discard (non-existing) | 6.9697 | 1.00x | Discard a value that doesn't exist |


## Test Information

- Date/Time: 2025-03-20 13:10:29
