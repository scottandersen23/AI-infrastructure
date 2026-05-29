# Benchmark Results

Phase 3 deliverable for recording local LLM benchmark runs.

## How To Run

Start the API wrapper:

```bash
cd 03-local-llm-serving-lab
LLM_RUNTIME=ollama DEFAULT_MODEL=llama3.2:3b uvicorn api.app.main:app --reload --port 8001
```

Run a benchmark:

```bash
python scripts/benchmark.py \
  --api-url http://localhost:8001 \
  --models llama3.2:3b mistral:7b \
  --requests 3 \
  --max-tokens 128
```

For smoke testing without a local model runtime:

```bash
LLM_RUNTIME=mock uvicorn api.app.main:app --reload --port 8001
python scripts/benchmark.py --models mock-local-model --requests 3
```

The script writes JSON and CSV files to `benchmark-runs/`, which is ignored by git so repeated local runs do not create repo noise.

## Benchmark Matrix

| Model            | Runtime   | Quantization            | Hardware      | Requests | Avg Latency | Tokens/sec | Notes                      |
| ---------------- | --------- | ----------------------- | ------------- | -------: | ----------: | ---------: | -------------------------- |
| `llama3.2:3b`    | Ollama    | Q4/Q5, runtime-selected | Local machine |      TBD |         TBD |        TBD | Recommended first baseline |
| `mistral:7b`     | Ollama    | Q4/Q5, runtime-selected | Local machine |      TBD |         TBD |        TBD | Compare quality vs latency |
| GGUF local model | llama.cpp | Q5                      | Local machine |      TBD |         TBD |        TBD | Use for quantization study |

## Metrics To Capture

| Metric            | Meaning                                         |
| ----------------- | ----------------------------------------------- |
| Average latency   | End-to-end request time from client perspective |
| P50 latency       | Typical latency for the benchmark set           |
| Max latency       | Worst request in the benchmark set              |
| Tokens/sec        | Completion throughput reported by the runtime   |
| Completion tokens | Number of generated tokens                      |
| Response chars    | Rough output size sanity check                  |

## Sample Output Shape

```json
{
  "summary": [
    {
      "model": "llama3.2:3b",
      "requests": 3,
      "avg_latency_ms": 1250.4,
      "p50_latency_ms": 1198.7,
      "max_latency_ms": 1401.2,
      "avg_tokens_per_second": 31.8
    }
  ]
}
```

## Interpretation Checklist

- If latency is high but tokens/sec is reasonable, prompt processing or cold start may dominate.
- If tokens/sec is low, the model may be too large for the available hardware or quantization.
- If first run is much slower, separate cold-start results from warm runs.
- If larger models produce better answers but much lower throughput, document the quality/speed tradeoff instead of only ranking by speed.
