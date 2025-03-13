# Advanced Promise Patterns

This guide covers advanced usage patterns for the NEAR Python SDK's Promises API.

## Promise Chaining

You can chain promises to create sequences of operations where each step depends on the result of the previous step. The chainable method design of the Promises API makes this especially elegant:

```python
from near_sdk_py import call, callback, Contract, PromiseResult

class ChainedCallsExample:
    @call
    def lookup_and_process(self, registry_contract_id: str, processor_contract_id: str, item_id: str):
        # First call the registry to get information
        registry = Contract(registry_contract_id)
        
        # Chain everything in one fluent sequence
        promise = registry.call("get_item_info", id=item_id)
            .then("process_and_forward", processor_id=processor_contract_id)
        
        return promise.value()
    
    @callback
    def process_and_forward(self, result: PromiseResult, processor_id: str):
        if not result.success:
            return {"success": False, "error": "Failed to get item info"}
        
        # Get the item info from the first call
        item_info = result.data
        
        # Make a call to the processor contract with the item info and chain the final callback
        processor = Contract(processor_id)
        final_promise = processor.call("process_item", info=item_info)
            .then("handle_final_result")
        
        return final_promise.value()
    
    @callback
    def handle_final_result(self, result: PromiseResult):
        if result.success:
            return {"success": True, "processed_data": result.data}
        else:
            return {"success": False, "error": "Processing failed"}
```

The method chaining syntax makes it clear how each step in the process leads to the next, creating a readable flow of asynchronous operations.

This pattern allows for creating complex workflows where each step builds on the results of previous steps.

## Batch Operations

Use `PromiseBatch` when you need to perform multiple operations on a contract in a single transaction:

```python
from near_sdk_py import call, callback, Context, ONE_TGAS
from near_sdk_py.promises import Promise, PromiseResult

class BatchExample:
    @call
    def execute_multiple_actions(self, target_contract_id: str):
        # Create a batch for the target contract
        batch = Promise.create_batch(target_contract_id)
        
        # Add multiple actions to the batch
        batch.function_call("clear_data", {})
        batch.function_call("set_value", {"key": "name", "value": "NEAR Python SDK"})
        batch.function_call("set_value", {"key": "version", "value": "1.0.0"})
        
        # Add a callback to handle the result
        promise = batch.then(Context.current_account_id()).function_call(
            "handle_batch_result",
            {},
            gas=10 * ONE_TGAS,
        )
        
        return promise.value()
    
    @callback
    def handle_batch_result(self, result: PromiseResult):
        if result.success:
            return {"success": True, "message": "Batch operations completed successfully"}
        else:
            return {"success": False, "error": "Batch operations failed"}
```

Batch operations have an important property: they **act as a unit**. If any function in the batch fails, they all get reverted.

## Working with Multiple Contracts in Parallel

Call different contracts in parallel and process all results together:

```python
from near_sdk_py import call, multi_callback, Contract
from near_sdk_py.promises import Promise, PromiseResult
from typing import List

class MultiContractExample:
    @call
    def aggregate_data(self, contract_ids: List[str], query: str):
        # Initialize an empty list to collect promises
        promises = []
        
        # Create promises for each contract
        for contract_id in contract_ids:
            contract = Contract(contract_id)
            promise = contract.call("search", query=query)
            promises.append(promise)
        
        # Join the first promise with the rest
        first_promise = promises[0]
        combined_promise = first_promise.join(
            promises[1:],
            "aggregate_results",
            query=query
        )
        
        return combined_promise.value()
    
    @multi_callback
    def aggregate_results(self, results: List[PromiseResult], query: str):
        # Combine results from all contracts
        all_data = []
        
        for i, result in enumerate(results):
            if result.success:
                all_data.append(result.data)
        
        return {
            "query": query,
            "total_results": len(all_data),
            "data": all_data
        }
```

When you run operations on different contracts in parallel, they execute independently. If one fails, the others will still execute and not be reverted.

## Using Contract Batches

The `Contract` class provides a convenient `batch()` method to create batches for a specific contract:

```python
from near_sdk_py import call, callback, Contract, PromiseResult, ONE_TGAS

class ContractBatchExample:
    @call
    def update_contract_state(self, contract_id: str, data: dict):
        # Create a contract instance
        contract = Contract(contract_id)
        
        # Create a batch for the contract
        batch = contract.batch()
        
        # Add operations to the batch
        batch.function_call("clear_old_data", {})
        
        # Add each key-value pair as a separate call
        for key, value in data.items():
            batch.function_call(
                "set_value", 
                {"key": key, "value": value},
                gas=5 * ONE_TGAS
            )
        
        # Add a callback
        promise = batch.then("on_update_complete")
        
        return promise.value()
    
    @callback
    def on_update_complete(self, result: PromiseResult):
        return {
            "success": result.success,
            "message": "State updated successfully" if result.success 
                       else "Failed to update state"
        }
```

## Dynamic Promise Construction

You can build complex promise chains dynamically based on input conditions:

```python
from near_sdk_py import call, callback, Contract, PromiseResult, ONE_TGAS
from typing import List, Dict

class DynamicPromiseExample:
    @call
    def process_workflow(self, steps: List[Dict], input_data: Dict):
        if not steps:
            return {"success": True, "data": input_data}
        
        # Get the first step
        first_step = steps[0]
        contract_id = first_step["contract"]
        method = first_step["method"]
        
        # Start the promise chain with the first step
        contract = Contract(contract_id)
        promise = contract.call(method, **input_data)
        
        # Store steps in a callback parameter for the next stage
        promise = promise.then(
            "continue_workflow", 
            remaining_steps=steps[1:],
            step_index=0,
            total_steps=len(steps)
        )
        
        return promise.value()
    
    @callback
    def continue_workflow(
        self, 
        result: PromiseResult, 
        remaining_steps: List[Dict],
        step_index: int,
        total_steps: int
    ):
        if not result.success:
            return {
                "success": False,
                "error": f"Step {step_index + 1} of {total_steps} failed",
                "step_result": result.data
            }
        
        # Get the result from the previous step
        current_data = result.data
        
        # If no more steps, we're done
        if not remaining_steps:
            return {
                "success": True,
                "data": current_data,
                "steps_completed": total_steps
            }
        
        # Get the next step
        next_step = remaining_steps[0]
        contract_id = next_step["contract"]
        method = next_step["method"]
        
        # Continue the chain with the next step
        contract = Contract(contract_id)
        promise = contract.call(method, **current_data)
        
        # Continue the workflow
        promise = promise.then(
            "continue_workflow",
            remaining_steps=remaining_steps[1:],
            step_index=step_index + 1,
            total_steps=total_steps
        )
        
        return promise.value()
```

This approach allows building dynamic workflows based on configuration or user input.

## Promise Composition Rules

When composing promises, remember these rules:

- ✅ Promises can be joined using `.join()` for parallel execution
- ✅ Promises can be chained with `.then()` for sequential execution
- ⛔ You cannot return a joint promise without a callback
- ⛔ You cannot use `.join()` within a `.then()`
- ⛔ You cannot use `.then()` within a `.then()`

Here's an example of correct promise composition:

```python
# Correct: Parallel execution with combined callback
promise1 = contract1.call("method1")
promise2 = contract2.call("method2")
promise3 = contract3.call("method3")

combined = promise1.join([promise2, promise3], "process_all_results")
return combined.value()

# Correct: Sequential execution
promise1 = contract1.call("method1")
promise2 = promise1.then("process_first_result")
promise3 = promise2.then("process_second_result")
return promise3.value()
```

## Next Steps

Now that you're familiar with advanced promise patterns, you might want to explore:

- [Account Operations](account-operations.md) for managing accounts and access keys
- [Error Handling](error-handling.md) for robust cross-contract interactions
- [Security Considerations](security.md) for secure cross-contract communication