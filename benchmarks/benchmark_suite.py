
import asyncio
import time
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aiagentsuite.core.suite import AIAgentSuite
from aiagentsuite.core.observability import get_global_observability_manager

# Configure logging to stdout so we can see it
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def run_benchmark():
    print("Starting AI Agent Suite Benchmark...")

    # Create a temporary directory for the memory bank
    temp_dir = tempfile.mkdtemp()
    print(f"Using temporary directory for memory bank: {temp_dir}")

    try:
        suite = AIAgentSuite()

        await suite.initialize()

        # Hack to redirect memory bank to temp dir
        if hasattr(suite, 'memory_bank'):
             suite.memory_bank.base_path = Path(temp_dir) / "memory-bank"
             # Ensure the directory exists
             (suite.memory_bank.base_path).mkdir(parents=True, exist_ok=True)


        # Initialize observability explicitly to enable tracing
        obs_manager = get_global_observability_manager()
        await obs_manager.initialize()

        iterations = 100

        # Benchmark: Log Decision
        start_time = time.time()
        for i in range(iterations):
            await suite.log_decision(
                f"Benchmark Decision {i}",
                "Benchmarking decision logging",
                {"iteration": i}
            )
        end_time = time.time()
        decision_time = end_time - start_time
        print(f"Log Decision: {iterations} ops in {decision_time:.4f}s ({iterations/decision_time:.2f} ops/s)")

        # Benchmark: Get Constitution
        start_time = time.time()
        for i in range(iterations):
            await suite.get_constitution()
        end_time = time.time()
        constitution_time = end_time - start_time
        print(f"Get Constitution: {iterations} ops in {constitution_time:.4f}s ({iterations/constitution_time:.2f} ops/s)")

        # Benchmark: List Protocols
        start_time = time.time()
        for i in range(iterations):
            await suite.list_protocols()
        end_time = time.time()
        protocol_time = end_time - start_time
        print(f"List Protocols: {iterations} ops in {protocol_time:.4f}s ({iterations/protocol_time:.2f} ops/s)")

        # Shutdown observability to flush traces
        await obs_manager.shutdown()

    finally:
        # Cleanup temporary directory
        shutil.rmtree(temp_dir)
        print("Cleaned up temporary directory.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
