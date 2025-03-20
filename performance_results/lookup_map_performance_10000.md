# LookupMap Performance Test Results

LookupMap size: 10000 elements

| Operation | Gas (TGas) | vs. Baseline | Details |
|-----------|------------|--------------|----------|
| hello world (baseline) | 6.9030 | 1.00x | Basic function call |
| contains_key (existing) | 6.8921 | 1.00x | Average of 6 keys |
| contains_key (non-existing) | 6.9277 | 1.00x | Check for a key that doesn't exist |
| get | 6.9733 | 1.01x | Average of 6 keys |
| set (update existing) | 7.2679 | 1.05x | Update value for an existing key |
| set (add new) | 7.7680 | 1.13x | Add value with a new key |
| remove | 7.9393 | 1.15x | Remove an existing key-value pair |


## Test Information

- Date/Time: 2025-03-20 11:31:47
