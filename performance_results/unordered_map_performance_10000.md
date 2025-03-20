# UnorderedSet Performance Test Results

UnorderedSet size: 10000 elements

| Operation | Gas (TGas) | vs. Baseline | Details |
|-----------|------------|--------------|----------|
| hello world (baseline) | 7.3869 | 1.00x | Basic function call |
| get_length | 7.6414 | 1.03x | Set size: 10000 |
| contains_value (item lookup) | 7.6056 | 1.03x | Average of 6 items |
|   - contains_value for item bulk_item_0 | 7.6008 | 1.03x | Direct lookup of item bulk_item_0 |
|   - contains_value for item bulk_item_1 | 7.6008 | 1.03x | Direct lookup of item bulk_item_1 |
|   - contains_value for item bulk_item_100 | 7.6066 | 1.03x | Direct lookup of item bulk_item_100 |
|   - contains_value for item bulk_item_999 | 7.6066 | 1.03x | Direct lookup of item bulk_item_999 |
|   - contains_value for item bulk_item_5000 | 7.6094 | 1.03x | Direct lookup of item bulk_item_5000 |
|   - contains_value for item bulk_item_9999 | 7.6093 | 1.03x | Direct lookup of item bulk_item_9999 |
| remove_item | 11.9519 | 1.62x | Removes item with value bulk_item_5000 |
| add_item (insert new) | 9.8328 | 1.33x | Inserts new item with value new_value |
| get_paginated_items (pagination) | 10.2286 | 1.38x | Retrieves first 5 items |


## Test Information

- Date/Time: 2025-03-20 13:04:36
