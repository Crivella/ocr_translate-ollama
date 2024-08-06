# Plugin ocr_translate_ollama

This is a plugin for [ocr_translate](https://github.com/Crivella/ocr_translate) that implements translations through [ollama](https://github.com/ollama/ollama) using Large Language Models (LLM)s.

## Usage

- Install this by running `pip install ocr_translate_ollama`
- Add `ocr_translate_ollama` to your `INSTALLED_APPS` in `settings.py`
- Run the server with `AUTOCREATE_VALIDATED_MODELS` once

## IMPORTANT

[Ollama](https://github.com/ollama/ollama) needs to be installed separately and reachable from the server (check the link for instructions).
The environment variable `OLLAMA_ENDPOINT` should be set to the endpoint of the ollama server (including the `/api`).

Example:

```bash
export OLLAMA_ENDPOINT=http://localhost:11434/api
```

Depending on the RAM available on your system (CPU/GPU), you also may need to tune the variables

- `OLLAMA_MAX_LOADED_MODELS`
- `OLLAMA_NUM_PARALLEL`

when running the server.

For more information, check the [ollama FAQ](https://github.com/ollama/ollama/blob/main/docs/faq.md)
