# UnorderedMap Performance Test Results

UnorderedMap size: 10000 elements

| Operation | Gas (TGas) | vs. Baseline | Details |
|-----------|------------|--------------|----------|
| hello world (baseline) | 7.3605 | 1.00x | Basic function call |
| get_length | 7.6064 | 1.03x | Map size: 10000 |
| get_item (key lookup) | 7.7197 | 1.05x | Average of 6 keys |
|   - get_item for key key_0 | 7.7107 | 1.05x | Direct lookup of key key_0 |
|   - get_item for key key_1 | 7.7106 | 1.05x | Direct lookup of key key_1 |
|   - get_item for key key_100 | 7.7220 | 1.05x | Direct lookup of key key_100 |
|   - get_item for key key_999 | 7.7219 | 1.05x | Direct lookup of key key_999 |
|   - get_item for key key_5000 | 7.7265 | 1.05x | Direct lookup of key key_5000 |
|   - get_item for key key_9999 | 7.7264 | 1.05x | Direct lookup of key key_9999 |
| contains_key | 7.5364 | 1.02x | Average of 6 keys |
| remove_item | 12.0747 | 1.64x | Removes item with key key_5000 |
| set_item (update existing) | 8.0630 | 1.10x | Updates existing item with key key_1 |
| set_item (insert new) | 9.9152 | 1.35x | Inserts new item with key key_new |


## Test Information

- Date/Time: 2025-03-20 09:17:51
