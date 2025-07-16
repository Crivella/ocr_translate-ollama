###################################################################################
# ocr_translate_ollama - a plugin for ocr_translate                               #
# Copyright (C) 2024-present Crivella                                             #
#                                                                                 #
# This program is free software: you can redistribute it and/or modify            #
# it under the terms of the GNU General Public License as published by            #
# the Free Software Foundation, either version 3 of the License.                  #
#                                                                                 #
# This program is distributed in the hope that it will be useful,                 #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                  #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                   #
# GNU General Public License for more details.                                    #
#                                                                                 #
# You should have received a copy of the GNU General Public License               #
# along with this program.  If not, see {http://www.gnu.org/licenses/}.           #
#                                                                                 #
# Home: https://github.com/Crivella/ocr_translate-ollama                          #
###################################################################################
"""Plugin to implement ollama (LLMs) based translations for ocr_translate"""

import logging
import os

import requests
from ocr_translate import models as m

from .commons import (DEFAULT_OLLAMA_ENDPOINT, MODEL_NAME_PREFIX,
                      MODELFILE_TPL, PROMPT_TPL)

logger = logging.getLogger('plugin')


class OllamaTSLModel(m.TSLModel):
    """TSLModel plugin to allow usage of ollama for translation."""
    class Meta:  # pylint: disable=missing-class-docstring
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        endpoint = os.getenv('OCT_OLLAMA_ENDPOINT', None)
        if endpoint is None:
            logger.warning(f'OCT_OLLAMA_ENDPOINT not set. Using default value `{DEFAULT_OLLAMA_ENDPOINT}`.')
            endpoint = DEFAULT_OLLAMA_ENDPOINT

        self.endpoint = endpoint

    def make_request(self, typ: str, url: str, data: dict = None, headers: dict = None) -> dict:
        """Make a request to the ollama server."""
        res = requests.request(typ, f'{self.endpoint}/{url}', json=data, headers=headers, timeout=120)
        if res.status_code != 200:
            logger.error(f'Failed to make request to ollama: {res.text}')
            raise requests.RequestException(f'Failed to make request to ollama: {res.text}')
        try:
            data = res.json()
        # Case of multiple json lines
        except Exception as exc:  # pylint: disable=bare-except
            body = res.content.decode('utf-8').replace('\n', '').replace(' ', '')
            if '"status":"success"' in body:
                return {'status': 'success'}
            raise requests.RequestException(f'Failed to parse response from ollama: {body}. Error: {exc}')
        return res.json()

    def get_version(self) -> tuple[int, int, int]:
        """Get the version of the ollama server.

        Returns:
            tuple[int, int, int]: Version of the ollama server.
        """
        version_data = self.make_request('GET', 'version') or {}
        version_str = version_data.get('version', '0.0.0')
        return tuple(map(int, version_str.split('.')))


    def get_model_list(self) -> list[dict]:
        """Get the list of models available inside ollama.

        Returns:
            list[dict]: List of models available in ollama.
        """
        return self.make_request('GET', 'tags').get('models', [])

    def load(self):
        """Check if model exists in ollama. In case not try to download it."""
        models = self.get_model_list()
        for model in models:
            name = model.get('name', '')
            if name == self.name:
                return

        logger.info(f'Model {self.name} not found in ollama, attempting download...')
        ollama_name = str(self.name).replace(f'{MODEL_NAME_PREFIX}_', '')
        data = {
            'name': ollama_name,
            'stream': False,
        }
        res = self.make_request('POST', 'pull', data)
        if res.get('status', 'error') != 'success':
            raise requests.RequestException(f'Failed to download model `{ollama_name}` from ollama.')

        logger.info(f'Model {self.name} downloaded successfully.')
        logger.info('Creating model with system prompt for translation.')

        version = self.get_version()
        if version <= (0, 5, 5):
            data = {
                'name': self.name,
                'modelfile': MODELFILE_TPL.format(model_name=ollama_name),
                'stream': False,
            }
        else:
            sys_prompt = '\n'.join(MODELFILE_TPL.splitlines()[2:-1])  # Remove the FROM and SYSTEM lines/delimiters
            data = {
                'name': self.name,
                'from': ollama_name,
                'system': sys_prompt,
                'stream': False,
            }
        res = self.make_request('POST', 'create', data)
        if res.get('status', 'error') != 'success':
            raise requests.RequestException(f'Failed to create custom model `{self.name}` in ollama.')

    def unload(self) -> None:
        """Unload the model from memory."""

    def _translate(
            self,
            tokens: list, src_lang: str, dst_lang: str, options: dict = None) -> str | list[str]:
        """Translate a text using a the loaded model.

        Args:
            tokens (list): list or list[list] of string tokens to be translated.
            lang_src (str): Source language.
            lang_dst (str): Destination language.
            options (dict, optional): Options for the translation. Defaults to {}.

        Raises:
            TypeError: If text is not a string or a list of strings.

        Returns:
            Union[str,list[str]]: Translated text. If text is a list, returns a list of translated strings.
        """
        if options is None:
            options = {}
        if not isinstance(tokens, list):
            raise TypeError('tokens must be a list of strings or a list of list of strings')

        batch = True
        if isinstance(tokens[0], str):
            batch = False
            tokens = [tokens]

        res = []
        for sentence in tokens:
            inp_text = '. '.join(sentence)
            prompt = PROMPT_TPL.format(src_lang=src_lang, dst_lang=dst_lang, context='', text=inp_text)

            data = {
                'model': self.name,
                'prompt': prompt.strip(),
                # "raw": True,
                'stream': False,
            }

            logger.debug(f'Translating text with request data `{data}`.')
            app = self.make_request('POST', 'generate', data)
            logger.debug(f'Received response from ollama: {app}')
            if not app.get('done', False):
                raise requests.RequestException(f'Failed to translate text with model `{self.name}`.')

            out_text = app.get('response')
            res.append(out_text)

        if not batch:
            res = res[0]

        return res
