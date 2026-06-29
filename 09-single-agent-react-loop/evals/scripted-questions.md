# Scripted Evaluation Questions

Use these prompts to compare single-shot RAG against the bounded ReAct loop.

| Scenario        | Question                                                        | Expected Tool Path             |
| --------------- | --------------------------------------------------------------- | ------------------------------ |
| Document search | Search the docs for AI platform reliability practices.          | `search_docs`                  |
| Metrics lookup  | Summarize current latency and reliability metrics.              | `get_metrics`                  |
| Combined task   | Search the docs and summarize reliability metrics.              | `search_docs` -> `get_metrics` |
| Job lookup      | Check the status of job `00000000-0000-0000-0000-000000000000`. | `get_job_status`               |
| No tool needed  | Explain what a bounded agent loop is.                           | none                           |

## Evaluation Notes

Track:

- Steps taken
- Tools invoked
- Latency per step
- Final answer groundedness
- Failure mode if Project 08 or capstone services are unavailable
