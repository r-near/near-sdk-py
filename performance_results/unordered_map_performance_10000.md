# UnorderedMap Performance Test Results

UnorderedMap size: 10000 elements

| Operation | Gas (TGas) | vs. Baseline | Details |
|-----------|------------|--------------|----------|
| hello world (baseline) | 7.3719 | 1.00x | Basic function call |
| get_length | 7.6193 | 1.03x | Map size: 10000 |
| get_item (key lookup) | 7.7334 | 1.05x | Average of 6 keys |
|   - get_item for key key_0 | 7.7244 | 1.05x | Direct lookup of key key_0 |
|   - get_item for key key_1 | 7.7244 | 1.05x | Direct lookup of key key_1 |
|   - get_item for key key_100 | 7.7357 | 1.05x | Direct lookup of key key_100 |
|   - get_item for key key_999 | 7.7357 | 1.05x | Direct lookup of key key_999 |
|   - get_item for key key_5000 | 7.7402 | 1.05x | Direct lookup of key key_5000 |
|   - get_item for key key_9999 | 7.7402 | 1.05x | Direct lookup of key key_9999 |
| contains_key | 7.5480 | 1.02x | Average of 6 keys |
| set_item (update existing) | 8.0764 | 1.10x | Updates existing item with key key_1 |
| set_item (insert new) | 9.5580 | 1.30x | Inserts new item with key key_new |


## Test Information

- Date/Time: 2025-03-20 08:58:03
