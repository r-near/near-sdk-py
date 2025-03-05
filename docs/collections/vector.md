# Vector

`Vector` is a persistent, ordered collection similar to Python's built-in `list`. It provides indexed access to elements and maintains the order of insertion.

## Features

- ✅ Indexed access (get/set by position)
- ✅ Ordered (maintains insertion order)
- ✅ Iterable (can loop through all elements)
- ✅ Slicing support `my_vector[1:5]`
- ✅ Efficient append and pop operations

## When to Use

Use `Vector` when you need:

- An ordered list of items
- Access to elements by their position (index)
- To maintain the order of insertion
- To frequently add or remove items from the end

## Import

```python
from near_sdk_py.collections import Vector
# OR
from near_sdk_py.collections.vector import Vector
```

## Creation

```python
# Create a new vector with a unique storage prefix
my_vector = Vector("prefix")

# With type hints (recommended)
from typing import List
my_vector: Vector[str] = Vector("prefix")
```

## Basic Operations

```python
# Add elements
my_vector.append("hello")
my_vector.append("world")

# Get by index (0-based)
first_item = my_vector[0]  # "hello"

# Update an element
my_vector[1] = "NEAR"

# Get length
length = len(my_vector)  # 2

# Check if empty
is_empty = my_vector.is_empty()  # False

# Iterate through elements
for item in my_vector:
    print(item)  # Prints "hello" then "NEAR"
```

## Methods

### Accessing Elements

```python
# Get element at index
item = my_vector[3]

# Get element at index with default value if out of bounds
item = my_vector.get(3, default="not found")

# Get a slice
items = my_vector[1:4]  # Elements at indices 1, 2, and 3
```

### Adding Elements

```python
# Add to the end
my_vector.append("new item")

# Add multiple items
my_vector.extend(["item1", "item2", "item3"])
```

### Removing Elements

```python
# Remove and return the last element
last = my_vector.pop()

# Remove and return element at specific index
third = my_vector.pop(2)  # Remove element at index 2

# Efficiently remove element by swapping with last element
# (Changes order but is more gas-efficient)
my_vector.swap_remove(1)  # Removes element at index 1
```

### Other Operations

```python
# Clear all elements
my_vector.clear()
```

## Performance Characteristics

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| Access by index (`v[i]`) | O(1) | Constant time |
| Append (`v.append(x)`) | O(1) | Constant time |
| Pop from end (`v.pop()`) | O(1) | Constant time |
| Pop from middle (`v.pop(i)`) | O(n) | Requires shifting elements |
| Swap remove (`v.swap_remove(i)`) | O(1) | Constant time but changes order |
| Clear (`v.clear()`) | O(n) | Linear in the number of elements |
| Iteration | O(n) | Linear in the number of elements |

## Storage Considerations

`Vector` stores each element separately in the contract's storage with keys based on the element's index. For example, with a prefix `"mylist"`:

- Element 0 is stored at key `"mylist:0"`
- Element 1 is stored at key `"mylist:1"`
- ...and so on

## Comparison with Native Python List

| Feature | Vector | Python List |
|---------|--------|-------------|
| Persistence | ✅ Persists to blockchain storage | ❌ In-memory only |
| Element access | ✅ O(1) | ✅ O(1) |
| Append | ✅ O(1) | ✅ O(1) |
| Insert at position | ❌ Not supported | ✅ O(n) |
| Delete at position | ✅ O(n) or O(1) with swap_remove | ✅ O(n) |
| Memory usage | ✅ Lazy loading (only loads accessed elements) | ❌ All elements in memory |

## Examples

### Simple Token List

```python
from near_sdk_py import call, view
from near_sdk_py.collections import Vector

class TokenRegistry:
    def __init__(self):
        self.tokens = Vector("tokens")
    
    @call
    def register_token(self, token_id: str) -> int:
        self.tokens.append(token_id)
        return len(self.tokens) - 1  # Return the index
    
    @view
    def get_token(self, index: int) -> str:
        return self.tokens[index]
    
    @view
    def get_all_tokens(self) -> list:
        return list(self.tokens)
    
    @view
    def get_tokens_paginated(self, from_index: int = 0, limit: int = 50) -> list:
        return self.tokens[from_index:from_index + limit]
```

### Removing Items Efficiently

```python
@call
def remove_token(self, index: int) -> str:
    if index >= len(self.tokens):
        raise IndexError("Token index out of range")
    
    # If it's the last item, simple pop is most efficient
    if index == len(self.tokens) - 1:
        return self.tokens.pop()
    
    # Otherwise, swap_remove is more gas-efficient than pop(index)
    # but will change the order
    return self.tokens.swap_remove(index)
```

### Working with Complex Objects

```python
from typing import Dict
from near_sdk_py.collections import Vector

# Vector of dictionaries
self.nft_metadata = Vector("nft_metadata")

# Add a complex object
self.nft_metadata.append({
    "title": "My NFT",
    "description": "A unique digital asset",
    "media": "https://example.com/image.png",
    "creator_id": "alice.near"
})

# Retrieve and update a complex object
metadata = self.nft_metadata[0]
metadata["views"] = metadata.get("views", 0) + 1
self.nft_metadata[0] = metadata
```

## Best Practices

1. **Use type hints** for better IDE support and code clarity:
   ```python
   from near_sdk_py.collections import Vector
   
   tokens: Vector[str] = Vector("tokens")
   scores: Vector[int] = Vector("scores")
   users: Vector[Dict[str, Any]] = Vector("users")
   ```

2. **Implement pagination** for public methods that may return many items:
   ```python
   @view
   def get_tokens(self, from_index: int = 0, limit: int = 50) -> list:
       return self.tokens[from_index:min(from_index + limit, len(self.tokens))]
   ```

3. **Consider using `swap_remove`** instead of `pop(index)` when order doesn't matter:
   ```python
   # O(n) operation, maintains order
   token = self.tokens.pop(index)
   
   # O(1) operation, doesn't maintain order
   token = self.tokens.swap_remove(index)
   ```

4. **Clear vectors explicitly** when no longer needed to get a storage refund:
   ```python
   self.temporary_data.clear()
   ```

5. **Avoid extremely large vectors** that need to be accessed in their entirety, as this can exceed gas limits. Consider using pagination or alternative data structures.