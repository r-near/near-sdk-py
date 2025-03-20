# Vector Performance Test Results

Vector size: 10000 elements

| Operation | Gas (TGas) | vs. Baseline | Details |
|-----------|------------|--------------|----------|
| hello world (baseline) | 6.7468 | 1.00x | Basic function call |
| get_length | 6.9997 | 1.04x | Vector size: 10000 |
| get_item (random access) | 7.2269 | 1.07x | Average of 6 positions |
|   - get_item at index 0 | 7.2171 | 1.07x | Direct access at position 0 |
|   - get_item at index 1 | 7.2217 | 1.07x | Direct access at position 1 |
|   - get_item at index 100 | 7.2290 | 1.07x | Direct access at position 100 |
|   - get_item at index 999 | 7.2289 | 1.07x | Direct access at position 999 |
|   - get_item at index 5000 | 7.2322 | 1.07x | Direct access at position 5000 |
|   - get_item at index 9999 | 7.2322 | 1.07x | Direct access at position 9999 |
| pop_item | 7.8561 | 1.16x | Removes last element |
| swap_remove_item | 8.3108 | 1.23x | Swaps with last element and removes |
| add_item | 8.0219 | 1.19x | Appends item to vector |


## Test Information

- Date/Time: 2025-03-20 08:39:15
