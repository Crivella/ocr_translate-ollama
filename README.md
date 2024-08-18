# Plugin ocr_translate_ollama

This is a plugin for [ocr_translate](https://github.com/Crivella/ocr_translate) that implements translations through [ollama](https://github.com/ollama/ollama) using Large Language Models (LLM)s.

## Usage

For versions of the server `<v0.6`

- Install this by running `pip install ocr_translate_ollama`
- Add `ocr_translate_ollama` to your `INSTALLED_APPS` in `settings.py`
- Run the server with `AUTOCREATE_VALIDATED_MODELS` once

For versions of the server `>=0.6`

- Install through the server plugin manager

## Ollama name prefixes

To avoid cluttering the ollama server (or having to set a dedicated one), the plugin will create new models from the original one (with a dedicated system prompt) adding the prefix `oct_ollama_` to the model names.

This behavior can be changed by setting the environment variable `OCT_OLLAMA_PREFIX` to a different value.

**NOTE**: The final `_` is added by the plugin, so it should not be included in the prefix.

## IMPORTANT

[Ollama](https://github.com/ollama/ollama) needs to be installed separately and reachable from the server (check the link for instructions).
The environment variable `OCT_OLLAMA_ENDPOINT` should be set to the endpoint of the ollama server (including the `/api`).

Example:

```bash
export OLLAMA_ENDPOINT=http://localhost:11434/api
```

Depending on the RAM available on your system (CPU/GPU), you also may need to tune the variables

- `OLLAMA_MAX_LOADED_MODELS`
- `OLLAMA_NUM_PARALLEL`

when running the server.

For more information, check the [ollama FAQ](https://github.com/ollama/ollama/blob/main/docs/faq.md)
