# TreeMap

`TreeMap` is a persistent, ordered map collection that keeps its keys in sorted order. It provides functionality similar to a sorted dictionary, with special operations for working with ordered data.

## Features

- ✅ Key-value storage (like a dictionary/map)
- ✅ Keys kept in sorted order
- ✅ Range queries (get keys within a range)
- ✅ Find nearest keys (floor/ceiling operations)
- ✅ Min/max key operations
- ✅ Iterable (keys are iterated in order)

## When to Use

Use `TreeMap` when you need:

- Keys to be maintained in sorted order
- Range-based queries (e.g., "all events between date X and Y")
- To find the nearest key that matches a condition
- To efficiently find minimum or maximum keys
- Ordered iteration through keys

## Import

```python
from near_sdk_py.collections import TreeMap
# OR
from near_sdk_py.collections.tree_map import TreeMap
```

## Creation

```python
# Create a new TreeMap with a unique storage prefix
my_map = TreeMap("prefix")

# With type hints (recommended)
from typing import Dict
time_events: TreeMap[int, str] = TreeMap("time_events")
```

## Basic Operations

```python
# Set values (similar to a regular dictionary)
my_map[5] = "five"
my_map[2] = "two"
my_map[8] = "eight"

# Get values
value = my_map[5]  # "five"

# Get with default for missing keys
value = my_map.get(10, "default")  # "default"

# Check if key exists
has_key = 5 in my_map  # True

# Remove a key
del my_map[5]
# OR
removed_value = my_map.remove(2)  # "two"

# Get length
length = len(my_map)  # 1

# Check if empty
is_empty = my_map.is_empty()  # False
```

## Special Ordered Operations

```python
# Add some data
my_map[10] = "ten"
my_map[20] = "twenty"
my_map[30] = "thirty"
my_map[40] = "forty"

# Get the minimum key
min_key = my_map.min_key()  # 10

# Get the maximum key
max_key = my_map.max_key()  # 40

# Floor key: greatest key less than or equal to the given key
floor = my_map.floor_key(25)  # 20
floor = my_map.floor_key(20)  # 20 (exact match)
floor = my_map.floor_key(5)   # None (no keys less than 5)

# Ceiling key: least key greater than or equal to the given key
ceiling = my_map.ceiling_key(25)  # 30
ceiling = my_map.ceiling_key(30)  # 30 (exact match)
ceiling = my_map.ceiling_key(45)  # None (no keys greater than 45)

# Range queries: get all keys in a range
# From 15 (inclusive) to 35 (exclusive)
keys_in_range = my_map.range(from_key=15, to_key=35)  # [20, 30]

# All keys from 25 onwards
keys_from = my_map.range(from_key=25)  # [30, 40]

# All keys up to 25
keys_to = my_map.range(to_key=25)  # [10, 20]
```

## Iteration

TreeMap iteration is always in key order:

```python
# Iterate through keys in ascending order
for key in my_map:
    print(key, my_map[key])
# Prints: 10 ten, 20 twenty, 30 thirty, 40 forty

# Get all keys in order
ordered_keys = my_map.keys()  # [10, 20, 30, 40]

# Get all values in key order
ordered_values = my_map.values()  # ["ten", "twenty", "thirty", "forty"]

# Get all key-value pairs in key order
ordered_items = my_map.items()  # [(10, "ten"), (20, "twenty"), (30, "thirty"), (40, "forty")]
```

### Reverse Iteration

To iterate in reverse order (highest to lowest):

```python
# Get keys and reverse them
keys = my_map.keys()
keys.reverse()

# Iterate through reversed keys
for key in keys:
    print(key, my_map[key])
# Prints: 40 forty, 30 thirty, 20 twenty, 10 ten
```

## Performance Characteristics

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| Get (`map[key]`) | O(log n) | Binary search to find key |
| Set (`map[key] = value`) | O(log n) | Binary search + insertion |
| Delete (`del map[key]`) | O(log n) | Binary search + removal |
| Contains (`key in map`) | O(log n) | Binary search |
| Min/Max Key | O(1) | Direct access to first/last key |
| Floor/Ceiling Key | O(log n) | Binary search |
| Range Query | O(log n + k) | Binary search + k elements in range |
| Iteration | O(n) | Visit all elements in order |

## Storage Implementation

`TreeMap` uses a `Vector` to store keys in sorted order, plus individual storage entries for each key-value pair:

- Keys Vector: Stored at `{prefix}:keys`
- Values: Stored at `{prefix}:{serialized_key}`
- Metadata: Stored at `{prefix}:meta`

## Comparison with UnorderedMap

| Feature | TreeMap | UnorderedMap |
|---------|---------|--------------|
| Key-value storage | ✅ | ✅ |
| Ordered keys | ✅ (sorted) | ❌ (insertion order) |
| Range queries | ✅ | ❌ |
| Floor/ceiling operations | ✅ | ❌ |
| Performance | ⚠️ O(log n) for most operations | ✅ O(1) for most operations |
| Memory overhead | ⚠️ Higher | ✅ Lower |

## Examples

### Time-Based Event Scheduling

```python
from near_sdk_py import call, view, Context
from near_sdk_py.collections import TreeMap
from typing import List, Dict, Optional

class EventScheduler:
    def __init__(self):
        # Map of timestamp -> event data
        self.events = TreeMap("events")
    
    @call
    def schedule_event(self, title: str, description: str, timestamp: int) -> Dict:
        """Schedule a new event at the specified timestamp"""
        event = {
            "title": title,
            "description": description,
            "timestamp": timestamp,
            "creator": Context.predecessor_account_id(),
            "created_at": Context.block_timestamp()
        }
        
        self.events[timestamp] = event
        return event
    
    @view
    def get_event(self, timestamp: int) -> Optional[Dict]:
        """Get an event by its exact timestamp"""
        return self.events.get(timestamp)
    
    @view
    def get_upcoming_events(self, limit: int = 10) -> List[Dict]:
        """Get upcoming events from current time"""
        current_time = Context.block_timestamp()
        
        # Find events with timestamps >= current_time
        upcoming = []
        count = 0
        
        for time in self.events.range(from_key=current_time):
            if count >= limit:
                break
            upcoming.append(self.events[time])
            count += 1
        
        return upcoming
    
    @view
    def get_events_in_timespan(self, start_time: int, end_time: int) -> List[Dict]:
        """Get all events scheduled between start_time and end_time"""
        events = []
        
        for time in self.events.range(from_key=start_time, to_key=end_time):
            events.append(self.events[time])
        
        return events
    
    @view
    def get_next_event(self) -> Optional[Dict]:
        """Get the next upcoming event"""
        current_time = Context.block_timestamp()
        
        # Find the first event with timestamp >= current_time
        next_time = self.events.ceiling_key(current_time)
        if next_time is not None:
            return self.events[next_time]
        
        return None
    
    @call
    def cancel_event(self, timestamp: int) -> bool:
        """Cancel an event by removing it"""
        if timestamp in self.events:
            event = self.events[timestamp]
            
            # Only allow the creator to cancel
            assert event["creator"] == Context.predecessor_account_id(), "Only the creator can cancel"
            
            del self.events[timestamp]
            return True
        
        return False
```

### Price Ordering in a Marketplace

```python
from near_sdk_py import call, view, Context
from near_sdk_py.collections import TreeMap, UnorderedMap
from typing import List, Dict, Optional

class Marketplace:
    def __init__(self):
        # Map of item_id -> item data
        self.items = UnorderedMap("items")
        
        # Map of price -> list of item_ids at that price
        self.items_by_price = TreeMap("items_by_price")
    
    @call
    def list_item(self, item_id: str, title: str, description: str, price: int) -> Dict:
        """List a new item for sale"""
        
        # Create item data
        item = {
            "item_id": item_id,
            "title": title,
            "description": description,
            "price": price,
            "seller": Context.predecessor_account_id(),
            "listed_at": Context.block_timestamp()
        }
        
        # Store in main items map
        self.items[item_id] = item
        
        # Also index by price
        items_at_price = self.items_by_price.get(price, [])
        items_at_price.append(item_id)
        self.items_by_price[price] = items_at_price
        
        return item
    
    @view
    def get_cheapest_items(self, limit: int = 10) -> List[Dict]:
        """Get the cheapest items available"""
        result = []
        count = 0
        
        for price in self.items_by_price:
            items_at_price = self.items_by_price[price]
            
            for item_id in items_at_price:
                if count >= limit:
                    break
                
                item = self.items[item_id]
                result.append(item)
                count += 1
            
            if count >= limit:
                break
        
        return result
    
    @view
    def get_items_in_price_range(self, min_price: int, max_price: int) -> List[Dict]:
        """Get items within a specific price range"""
        result = []
        
        for price in self.items_by_price.range(from_key=min_price, to_key=max_price+1):
            items_at_price = self.items_by_price[price]
            
            for item_id in items_at_price:
                item = self.items[item_id]
                result.append(item)
        
        return result
    
    @view
    def find_items_at_budget(self, budget: int) -> List[Dict]:
        """Find items at or below a certain budget"""
        # Find highest price that fits budget
        max_affordable_price = self.items_by_price.floor_key(budget)
        
        if max_affordable_price is None:
            return []  # No affordable items
        
        # Get all items at or below that price
        return self.get_items_in_price_range(0, max_affordable_price)
```

### Version Control System

```python
from near_sdk_py import call, view, Context
from near_sdk_py.collections import TreeMap, UnorderedMap
from typing import List, Dict, Optional

class VersionControl:
    def __init__(self):
        # Document contents by version number
        self.document_versions = TreeMap("document_versions")
        
        # Metadata about each version
        self.version_metadata = UnorderedMap("version_metadata")
        
        # Current version number
        self.current_version = 0
    
    @call
    def commit_version(self, content: str, message: str) -> int:
        """Commit a new version of the document"""
        # Increment version
        self.current_version += 1
        version = self.current_version
        
        # Store content
        self.document_versions[version] = content
        
        # Store metadata
        metadata = {
            "version": version,
            "author": Context.predecessor_account_id(),
            "timestamp": Context.block_timestamp(),
            "message": message
        }
        self.version_metadata[str(version)] = metadata
        
        return version
    
    @view
    def get_version(self, version: int) -> Dict:
        """Get a specific version of the document"""
        if version not in self.document_versions:
            raise ValueError("Version does not exist")
        
        content = self.document_versions[version]
        metadata = self.version_metadata[str(version)]
        
        return {
            "content": content,
            "metadata": metadata
        }
    
    @view
    def get_latest_version(self) -> Dict:
        """Get the latest version of the document"""
        if self.current_version == 0:
            return {"content": "", "metadata": None}
        
        return self.get_version(self.current_version)
    
    @view
    def get_version_history(self, limit: int = 10) -> List[Dict]:
        """Get recent version history, newest first"""
        if self.current_version == 0:
            return []
        
        # Get versions in descending order
        versions = []
        for i in range(self.current_version, max(0, self.current_version - limit), -1):
            metadata = self.version_metadata[str(i)]
            versions.append(metadata)
        
        return versions
    
    @view
    def find_version_before_time(self, timestamp: int) -> Optional[int]:
        """Find the latest version created before the given timestamp"""
        if self.current_version == 0:
            return None
        
        # We need to search through metadata to find version by timestamp
        # This is less efficient than storing by timestamp directly
        for i in range(self.current_version, 0, -1):
            metadata = self.version_metadata[str(i)]
            if metadata["timestamp"] <= timestamp:
                return i
        
        return None
```

## Best Practices

1. **Use for ordered data**: Only use `TreeMap` when you actually need ordered keys or range operations. For basic key-value storage, `UnorderedMap` is more efficient.

2. **Use type hints** for better IDE support and code clarity:
   ```python
   from near_sdk_py.collections import TreeMap
   
   events: TreeMap[int, Dict] = TreeMap("events")
   ```

3. **Consider key types carefully**: Keys must be comparable (support ordering with `<`, `>`, `==`). Strings, numbers, and other primitive types work well.

4. **Be mindful of complexity**: Remember that most operations are O(log n), which is acceptable for moderate-sized collections but not as efficient as O(1) operations in `UnorderedMap`.

5. **Use secondary indices** for complex queries: Like in the marketplace example, you might want to maintain both a main map and a `TreeMap` as a secondary index.

6. **Avoid duplicate keys**: If you need multiple items with the same key (like multiple events at the same timestamp), store a list of items at that key rather than trying to insert duplicate keys.

7. **Consider composite keys** for multi-dimensional ordering:
   ```python
   # For ordering by category and then by price
   composite_key = f"{category}:{price:010d}"  # Pad price for correct string ordering
   self.items[composite_key] = item
   ```

## Common Patterns

### Range Pagination

```python
@view
def get_events_paginated(self, start_time: int, limit: int = 10) -> Dict:
    """Get events starting from a specific time, with pagination"""
    events = []
    count = 0
    
    # Get the next key to continue from
    next_key = None
    
    for time in self.events.range(from_key=start_time):
        if count >= limit:
            next_key = time
            break
        
        events.append(self.events[time])
        count += 1
    
    return {
        "events": events,
        "next_time": next_key  # Return this for the next page query
    }
```

### Tiered Pricing

```python
class TieredPricing:
    def __init__(self):
        # Map of quantity threshold -> price per unit
        self.price_tiers = TreeMap("price_tiers")
        
        # Initialize with some tiers
        self.price_tiers[1] = 100      # 1+ units: $100 each
        self.price_tiers[10] = 90      # 10+ units: $90 each
        self.price_tiers[50] = 80      # 50+ units: $80 each
        self.price_tiers[100] = 70     # 100+ units: $70 each
    
    @view
    def get_price_per_unit(self, quantity: int) -> int:
        """Get the price per unit for a specific quantity"""
        # Find the highest tier that quantity exceeds
        tier_threshold = self.price_tiers.floor_key(quantity)
        
        if tier_threshold is None:
            # No tier found, use default price
            return 100
        
        return self.price_tiers[tier_threshold]
```

### Nearest Match Finder

```python
@view
def find_nearest_available_slot(self, preferred_time: int) -> Dict:
    """Find the nearest available time slot to the preferred time"""
    # Try exact match first
    if preferred_time in self.available_slots:
        return {
            "slot_time": preferred_time,
            "exact_match": True
        }
    
    # Try after preferred time
    after = self.available_slots.ceiling_key(preferred_time)
    
    # Try before preferred time
    before = self.available_slots.floor_key(preferred_time)
    
    if after is None and before is None:
        return {"error": "No available slots"}
    
    if after is None:
        return {
            "slot_time": before,
            "exact_match": False,
            "difference": preferred_time - before
        }
    
    if before is None:
        return {
            "slot_time": after,
            "exact_match": False,
            "difference": after - preferred_time
        }
    
    # Choose the closest one
    after_diff = after - preferred_time
    before_diff = preferred_time - before
    
    if after_diff < before_diff:
        return {
            "slot_time": after,
            "exact_match": False,
            "difference": after_diff
        }
    else:
        return {
            "slot_time": before,
            "exact_match": False,
            "difference": before_diff
        }
```

## Conclusion

`TreeMap` provides powerful functionality for working with ordered data in your NEAR smart contracts. While not as efficient as `UnorderedMap` for basic key-value storage, it excels in scenarios requiring sorted keys, range queries, or finding nearest matches. Use it when these capabilities are essential to your application logic.