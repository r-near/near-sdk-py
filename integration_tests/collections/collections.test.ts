import { test, describe, expect, beforeAll, afterAll } from 'vitest';
import { Worker, type NearAccount, Gas } from 'near-workspaces';
import { readFileSync } from 'node:fs';
import path from 'node:path';

// Define collection types
enum Collection {
    LOOKUP_MAP = "LookupMap",
    LOOKUP_SET = "LookupSet",
    TREE_MAP = "TreeMap",
    VECTOR = "Vector",
    UNORDERED_MAP = "UnorderedMap",
}

const GAS_LIMIT = Gas.parse('300 TGas');

describe('Python SDK Collections Tests', () => {
    let worker: Worker;
    let contract: NearAccount;
    let caller: NearAccount;

    // Set up the worker and deploy contract once before all tests
    beforeAll(async () => {
        // Initialize the sandbox environment
        worker = await Worker.init();

        // Create a test account
        const root = worker.rootAccount;
        contract = await root.createSubAccount('collections-test');
        caller = await root.createSubAccount('caller');

        // Deploy the contract
        const wasmPath = path.join(__dirname, '../collections/contract.wasm');
        await contract.deploy(readFileSync(wasmPath));

        // Initialize the contract
        await caller.call(contract, 'new', {});
    });

    // Clean up after all tests are done
    afterAll(async () => {
        await worker.tearDown();
    });

    // Test insert operation for each collection with a smaller number of items
    test('should insert items into collections', async () => {
        // Reduce item count to avoid gas issues
        const itemCount = 5;

        // Test each collection type separately
        for (const collection of Object.values(Collection)) {
            try {
                // Insert items with more gas
                const result = await caller.call(
                    contract,
                    'insert',
                    {
                        col: collection,
                        index_offset: 0,
                        iterations: itemCount
                    },
                    { gas: GAS_LIMIT }
                );

                // Verify correct number of items were inserted
                expect(result).toBe(itemCount + 1); // +1 because iterations is inclusive
                console.log(`Successfully inserted ${itemCount + 1} items into ${collection}`);
            } catch (error) {
                console.error(`Error inserting into ${collection}:`, error);
                throw error;
            }
        }
    });

    // Test the contains operation with minimal operations
    test('should check if items exist in collections', async () => {
        // Only test collections that support contains
        const testCollections = [
            Collection.LOOKUP_MAP,
            Collection.LOOKUP_SET,
            Collection.TREE_MAP,
            Collection.UNORDERED_MAP
        ];

        for (const collection of testCollections) {
            try {
                const result = await caller.call(
                    contract,
                    'contains',
                    {
                        col: collection,
                        repeat: 1,       // Minimal repeat
                        iterations: 2    // Very few iterations
                    },
                    { gas: GAS_LIMIT }
                );

                expect(result).toBe(true);
                console.log(`Successfully tested contains operation for ${collection}`);
            } catch (error) {
                console.error(`Error checking contains for ${collection}:`, error);
                throw error;
            }
        }
    });

    // Test basic remove operation
    test('should remove items from collections', async () => {
        // Reduce remove count
        const removeCount = 2;

        for (const collection of Object.values(Collection)) {
            try {
                const result = await caller.call(
                    contract,
                    'remove',
                    {
                        col: collection,
                        iterations: removeCount
                    },
                    { gas: GAS_LIMIT }
                );

                expect(result).toBe(removeCount + 1); // +1 because iterations is inclusive
                console.log(`Successfully removed ${removeCount + 1} items from ${collection}`);
            } catch (error) {
                console.error(`Error removing from ${collection}:`, error);
                throw error;
            }
        }
    });

    // Measure gas consumption for a single insert per collection
    test('should measure gas consumption for single insert', async () => {
        const results = {};

        for (const collection of Object.values(Collection)) {
            try {
                // Call with raw access to get gas metrics, but only insert ONE item
                const result = await caller.callRaw(
                    contract,
                    'insert',
                    {
                        col: collection,
                        index_offset: 100, // Use different offset to avoid conflicts
                        iterations: 1      // Just one item
                    },
                    { gas: GAS_LIMIT }
                );

                // Store gas consumption in TGas for comparison
                const gasInTGas = Number(result.gas_burnt) / 10 ** 12;
                results[collection] = `${gasInTGas.toFixed(2)} TGas`;

                // Just make sure the call succeeded - check status rather than succeeded flag
                expect(result.status).toContain('SuccessValue');
            } catch (error) {
                console.error(`Error measuring gas for ${collection}:`, error);
                throw error;
            }
        }

        // Log gas consumption for comparison
        console.table(results);
    });
});