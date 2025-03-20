# UnorderedMap Performance Test Results

UnorderedMap size: 10000 elements

| Operation | Gas (TGas) | vs. Baseline | Details |
|-----------|------------|--------------|----------|
| hello world (baseline) | 7.0430 | 1.00x | Basic function call |
| get_length | 7.2982 | 1.04x | Map size: 10000 |
| get_item (key lookup) | 7.8265 | 1.11x | Average of 6 keys |
|   - get_item for key key_0 | 7.8082 | 1.11x | Direct lookup of key key_0 |
|   - get_item for key key_1 | 7.8164 | 1.11x | Direct lookup of key key_1 |
|   - get_item for key key_100 | 7.8304 | 1.11x | Direct lookup of key key_100 |
|   - get_item for key key_999 | 7.8304 | 1.11x | Direct lookup of key key_999 |
|   - get_item for key key_5000 | 7.8367 | 1.11x | Direct lookup of key key_5000 |
|   - get_item for key key_9999 | 7.8369 | 1.11x | Direct lookup of key key_9999 |
| contains_key | 7.2347 | 1.03x | Average of 6 keys |
| remove_item | 12.3361 | 1.75x | Removes item with key key_5000 |
| set_item (update existing) | 8.1714 | 1.16x | Updates existing item with key key_1 |
| set_item (insert new) | 9.8489 | 1.40x | Inserts new item with key key_new |


## Test Information

- Date/Time: 2025-03-20 11:04:43
