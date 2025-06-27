"""
Performance benchmarking script for the GenAI Email Processing System.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import concurrent.futures
from dataclasses import dataclass

# For demo purposes, we'll create a simplified benchmark


@dataclass
class BenchmarkResult:
    """Results from a benchmark test."""
    test_name: str
    total_requests: int
    total_time: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    success_rate: float
    errors: List[str]


class EmailProcessingBenchmark:
    """Benchmark the email processing system."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def benchmark_classification(self, num_requests: int = 100) -> BenchmarkResult:
        """Benchmark email classification performance."""
        print(f"🔍 Benchmarking email classification ({num_requests} requests)...")
        
        sample_email = {
            "subject": "Issue with my order",
            "body": "I have a problem with my recent order. The item I received doesn't match what I ordered.",
            "sender": "customer@example.com"
        }
        
        response_times = []
        errors = []
        
        start_time = time.time()
        
        for i in range(num_requests):
            request_start = time.time()
            
            try:
                # Simulate classification processing time
                await asyncio.sleep(0.1 + (i % 10) * 0.01)  # Vary between 0.1-0.2 seconds
                response_time = time.time() - request_start
                response_times.append(response_time)
                
                if i % 10 == 0:
                    print(f"   Processed {i+1}/{num_requests} requests")
                    
            except Exception as e:
                errors.append(str(e))
        
        total_time = time.time() - start_time
        
        return BenchmarkResult(
            test_name="Email Classification",
            total_requests=num_requests,
            total_time=total_time,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            requests_per_second=len(response_times) / total_time,
            success_rate=(len(response_times) / num_requests) * 100,
            errors=errors
        )
    
    async def benchmark_response_generation(self, num_requests: int = 50) -> BenchmarkResult:
        """Benchmark response generation performance."""
        print(f"💬 Benchmarking response generation ({num_requests} requests)...")
        
        response_times = []
        errors = []
        
        start_time = time.time()
        
        for i in range(num_requests):
            request_start = time.time()
            
            try:
                # Simulate response generation processing time (typically slower)
                await asyncio.sleep(0.5 + (i % 5) * 0.1)  # Vary between 0.5-1.0 seconds
                response_time = time.time() - request_start
                response_times.append(response_time)
                
                if i % 5 == 0:
                    print(f"   Generated {i+1}/{num_requests} responses")
                    
            except Exception as e:
                errors.append(str(e))
        
        total_time = time.time() - start_time
        
        return BenchmarkResult(
            test_name="Response Generation",
            total_requests=num_requests,
            total_time=total_time,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            requests_per_second=len(response_times) / total_time,
            success_rate=(len(response_times) / num_requests) * 100,
            errors=errors
        )
    
    async def benchmark_concurrent_processing(self, num_concurrent: int = 10) -> BenchmarkResult:
        """Benchmark concurrent request processing."""
        print(f"🚀 Benchmarking concurrent processing ({num_concurrent} concurrent requests)...")
        
        async def process_single_request(request_id: int):
            """Process a single request."""
            start_time = time.time()
            
            # Simulate processing with some variation
            processing_time = 0.2 + (request_id % 5) * 0.05
            await asyncio.sleep(processing_time)
            
            return time.time() - start_time
        
        start_time = time.time()
        
        # Create concurrent tasks
        tasks = [process_single_request(i) for i in range(num_concurrent)]
        
        try:
            response_times = await asyncio.gather(*tasks)
            errors = []
        except Exception as e:
            response_times = []
            errors = [str(e)]
        
        total_time = time.time() - start_time
        
        return BenchmarkResult(
            test_name="Concurrent Processing",
            total_requests=num_concurrent,
            total_time=total_time,
            avg_response_time=statistics.mean(response_times) if response_times else 0,
            min_response_time=min(response_times) if response_times else 0,
            max_response_time=max(response_times) if response_times else 0,
            requests_per_second=len(response_times) / total_time if total_time > 0 else 0,
            success_rate=(len(response_times) / num_concurrent) * 100,
            errors=errors
        )
    
    def print_benchmark_results(self, result: BenchmarkResult):
        """Print formatted benchmark results."""
        print(f"\n📊 {result.test_name} Results:")
        print("─" * 50)
        print(f"Total Requests:      {result.total_requests}")
        print(f"Total Time:          {result.total_time:.2f} seconds")
        print(f"Requests/Second:     {result.requests_per_second:.2f}")
        print(f"Success Rate:        {result.success_rate:.1f}%")
        print(f"Avg Response Time:   {result.avg_response_time:.3f} seconds")
        print(f"Min Response Time:   {result.min_response_time:.3f} seconds")
        print(f"Max Response Time:   {result.max_response_time:.3f} seconds")
        
        if result.errors:
            print(f"Errors:              {len(result.errors)}")
            for error in result.errors[:3]:  # Show first 3 errors
                print(f"  - {error}")
            if len(result.errors) > 3:
                print(f"  ... and {len(result.errors) - 3} more")
    
    async def run_full_benchmark(self):
        """Run all benchmark tests."""
        print("⚡ GenAI Email Processing System - Performance Benchmark")
        print("=" * 60)
        
        results = []
        
        # Classification benchmark
        classification_result = await self.benchmark_classification(100)
        self.print_benchmark_results(classification_result)
        results.append(classification_result)
        
        # Response generation benchmark
        response_result = await self.benchmark_response_generation(50)
        self.print_benchmark_results(response_result)
        results.append(response_result)
        
        # Concurrent processing benchmark
        concurrent_result = await self.benchmark_concurrent_processing(20)
        self.print_benchmark_results(concurrent_result)
        results.append(concurrent_result)
        
        # Summary
        print("\n📈 Benchmark Summary:")
        print("=" * 60)
        for result in results:
            print(f"{result.test_name:25} | {result.requests_per_second:8.2f} req/s | {result.success_rate:6.1f}% success")
        
        print("\n✅ Benchmark completed!")
        print("\nNotes:")
        print("- This is a simulated benchmark for demonstration")
        print("- Actual performance will depend on hardware, network, and API latency")
        print("- For production benchmarking, use real API endpoints")
        
        return results


async def main():
    """Run the benchmark."""
    benchmark = EmailProcessingBenchmark()
    await benchmark.run_full_benchmark()


if __name__ == "__main__":
    asyncio.run(main())
