"""
ShopPilot AI - Performance Benchmarking Script
Measures actual latency across Search, Ranking, and Agent execution over 100 iterations.
"""

import time
import statistics
from backend.search import search_engine
from backend.ranking import ranking_engine
from backend.agent import agent
from backend.schema import ChatRequest, ExtractedRequirement


def benchmark_search():
    latencies = []
    for _ in range(100):
        t0 = time.perf_counter()
        search_engine.search(
            category="Laptop",
            max_price=75000.0,
            brands=["Lenovo", "ASUS", "Dell"],
            min_rating=4.2,
            required_features=["16GB RAM"],
            top_n=10,
        )
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)  # ms
    return {
        "mean_ms": round(statistics.mean(latencies), 3),
        "median_ms": round(statistics.median(latencies), 3),
        "p95_ms": round(statistics.quantiles(latencies, n=20)[18], 3),
        "min_ms": round(min(latencies), 3),
        "max_ms": round(max(latencies), 3),
    }


def benchmark_ranking():
    prods = search_engine.search(top_n=50)
    req = ExtractedRequirement(category="Laptop", max_price=70000.0, required_features=["16GB RAM"])
    latencies = []
    for _ in range(100):
        t0 = time.perf_counter()
        ranking_engine.rank_products(prods, req, top_n=5)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)
    return {
        "mean_ms": round(statistics.mean(latencies), 3),
        "median_ms": round(statistics.median(latencies), 3),
        "p95_ms": round(statistics.quantiles(latencies, n=20)[18], 3),
        "min_ms": round(min(latencies), 3),
        "max_ms": round(max(latencies), 3),
    }


def benchmark_agent():
    latencies = []
    req = ChatRequest(message="I need a laptop under 70000 for programming with 16GB RAM", session_id="bench_session")
    for _ in range(100):
        t0 = time.perf_counter()
        agent.process_message(req)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)
    return {
        "mean_ms": round(statistics.mean(latencies), 3),
        "median_ms": round(statistics.median(latencies), 3),
        "p95_ms": round(statistics.quantiles(latencies, n=20)[18], 3),
        "min_ms": round(min(latencies), 3),
        "max_ms": round(max(latencies), 3),
    }


if __name__ == "__main__":
    print("--- Running ShopPilot AI Latency Benchmarks (100 Iterations Each) ---")
    s_res = benchmark_search()
    print(f"Deterministic Search Latency: Mean = {s_res['mean_ms']} ms | Median = {s_res['median_ms']} ms | P95 = {s_res['p95_ms']} ms")

    r_res = benchmark_ranking()
    print(f"Ranking Engine Latency:       Mean = {r_res['mean_ms']} ms | Median = {r_res['median_ms']} ms | P95 = {r_res['p95_ms']} ms")

    a_res = benchmark_agent()
    print(f"End-to-End Agent Latency:    Mean = {a_res['mean_ms']} ms | Median = {a_res['median_ms']} ms | P95 = {a_res['p95_ms']} ms")
