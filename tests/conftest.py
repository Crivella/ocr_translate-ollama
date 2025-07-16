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
"""Tests for the ocr_translate-ollama plugin."""

# pylint: disable=unused-argument

import pytest

from ocr_translate_ollama import commons, plugin


@pytest.fixture(scope='function')
def mock_translate():
    """Mock of the googletrans Translator."""
    class Result():
        """Mock the output"""
        def __init__(self):
            self.text = None

    def mock_function(text, *args, src, dest):
        res = Result()
        res.text = text
        mock_function.called = True
        mock_function.args = (text,)
        mock_function.kwargs = {'src': src, 'dest': dest}

        return res

    return mock_function

@pytest.fixture(scope='module')
def model_base_name() -> str:
    """Model name."""
    return 'llama3:8b'

@pytest.fixture(scope='module')
def model_name(model_base_name) -> str:
    """Model name."""
    return f'{commons.MODEL_NAME_PREFIX}_{model_base_name}'

@pytest.fixture(scope='function')
def model(model_name) -> plugin.OllamaTSLModel:
    """Generate a model."""
    res = plugin.OllamaTSLModel(name=model_name)
    res.save()
    return res

@pytest.fixture(scope='function')
def endpoint() -> str:
    """Set endpoint."""
    return 'http://random.com'

@pytest.fixture(scope='function')
def env_endpoint(monkeypatch, endpoint):
    """Set environment variable for endpoint."""
    monkeypatch.setenv('OCT_OLLAMA_ENDPOINT', endpoint)
