# What broke

Kept from hour one. Each entry: what happened, why, what changed.

## 27 Oct, 01:40 IST: no open-model key on the machine
Every OpenAI-compatible open-model key found locally failed. One Gemini project's prepaid credits were depleted (HTTP 402), and two other Gemini keys were invalid. Ready was built so that the model only ranks and phrases, never decides, so it degrades to repo search alone. The eval runs the grep-only variant first, which also becomes the baseline row the model has to beat.

## 27 Oct, 01:10 IST: the machine slowed to a crawl
`uv sync` and even `Get-Process` took over two minutes, with about 20 python and uv processes left over from earlier sessions. Long jobs moved to background runs and to the worker session.
