# UnorderedMap Performance Test Results

UnorderedMap size: 10000 elements

| Operation | Gas (TGas) | vs. Baseline | Details |
|-----------|------------|--------------|----------|
| hello world (baseline) | 7.4012 | 1.00x | Basic function call |
| get_length | 7.6488 | 1.03x | Map size: 10000 |
| get_item (key lookup) | 7.7610 | 1.05x | Average of 6 keys |
|   - get_item for key key_0 | 7.7520 | 1.05x | Direct lookup of key key_0 |
|   - get_item for key key_1 | 7.7520 | 1.05x | Direct lookup of key key_1 |
|   - get_item for key key_100 | 7.7632 | 1.05x | Direct lookup of key key_100 |
|   - get_item for key key_999 | 7.7632 | 1.05x | Direct lookup of key key_999 |
|   - get_item for key key_5000 | 7.7677 | 1.05x | Direct lookup of key key_5000 |
|   - get_item for key key_9999 | 7.7677 | 1.05x | Direct lookup of key key_9999 |
| contains_key | 7.5777 | 1.02x | Average of 6 keys |
| remove_item | 12.0511 | 1.63x | Removes item with key key_5000 |
| set_item (update existing) | 8.1054 | 1.10x | Updates existing item with key key_1 |
| set_item (insert new) | 9.9539 | 1.34x | Inserts new item with key key_new |
| get_items (pagination) | 11.1290 | 1.50x | Retrieves first 5 items |


## Test Information

- Date/Time: 2025-03-20 11:30:54
