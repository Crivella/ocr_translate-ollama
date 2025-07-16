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
# Home: https://github.com/Crivella/ocr_translate-google                          #
###################################################################################
"""Tests for the ocr_translate-ollama plugin."""

# pylint: disable=missing-function-docstring,missing-class-docstring,protected-access

from importlib.metadata import entry_points

import pytest
import requests

import ocr_translate_ollama as octo
import ocr_translate_ollama.plugin as octo_plugin

pytestmark = pytest.mark.django_db

@pytest.fixture(scope='function')
def resp():
    """Mock the content of a requests.Response."""
    return []

@pytest.fixture()
def mock_content():
    """Mock the content of a requests.Response."""
    return b'{}'

@pytest.fixture(autouse=True)
def mock_request(request, monkeypatch, mock_content, resp):
    """Mock the get method of requests."""
    scode = getattr(request, 'param', {}).get('status_code', [200]*50)
    content = getattr(request, 'param', {}).get('content', [mock_content]*50)

    def mock_function(*args, **kwargs):
        res = requests.Response()
        res.status_code = scode.pop(0)
        res._content = content.pop(0) # pylint: disable=protected-access
        res._args = args # pylint: disable=protected-access
        res._kwargs = kwargs
        resp.append(res)

        return res

    monkeypatch.setattr(octo_plugin.requests, 'request', mock_function)

def test_entrypoint():
    """The entrypoint defined in the model should not be changed."""
    # Updating the pluging with a change in entrypoint would break the app unless model entries are regenerated.
    # This restriction might be released in the future.
    assert octo.tsl_model_data['entrypoint'] == 'ollama.tsl'

def test_entrypoint_pyproj():
    """The entrypoint defined for the model data should match the one exported in pyproject.toml."""
    ept_group = 'ocr_translate.tsl_models'
    ept_name = octo.tsl_model_data['entrypoint']
    for ept in entry_points(group=ept_group, name=ept_name):
        cls = ept.load()

    assert cls is octo_plugin.OllamaTSLModel

@pytest.mark.parametrize('mock_request', [{'status_code': [400]}], indirect=True)
def test_make_request_fail(model):
    """Test failed request."""
    with pytest.raises(requests.RequestException, match=r'^Failed to make request to ollama.*'):
        model.make_request('GET', 'test')

def test_make_request_success(resp, model):
    """Test successful request."""
    typ = 'SOME'
    url = 'test'
    model.make_request(typ, url)
    res = resp.pop()
    assert res._args[0] == typ
    assert res._args[1] == octo_plugin.DEFAULT_OLLAMA_ENDPOINT + '/' + url

@pytest.mark.parametrize(
        'mock_request', [{
            'status_code': [200,],
            'content': [b'{"something": "else"}\n{ "status": "success" }',]
        }],
        indirect=True
    )
def test_make_request_success_multilinejson(resp, model):
    """Test successful request."""
    typ = 'SOME'
    url = 'test'
    model.make_request(typ, url)
    res = resp.pop()
    assert res._args[0] == typ
    assert res._args[1] == octo_plugin.DEFAULT_OLLAMA_ENDPOINT + '/' + url

@pytest.mark.parametrize(
        'mock_request', [{
            'status_code': [200,],
            'content': [b'{"something": "else"}\n{ "status": "non-success" }',]
        }],
        indirect=True
    )
def test_make_request_failw_multilinejson(resp, model):
    """Test successful request."""
    typ = 'SOME'
    url = 'test'
    with pytest.raises(requests.RequestException, match=r'^Failed to parse response from ollama:.*'):
        model.make_request(typ, url)

def test_get_model_list_noenv(resp, model):
    """Test that the model list is returned correctly."""
    endpoint = octo_plugin.DEFAULT_OLLAMA_ENDPOINT
    res = model.get_model_list()

    assert isinstance(res, list)
    res = resp.pop()
    assert res._args[0] == 'GET'
    assert res._args[1] == endpoint + '/tags'

    assert len(resp) == 0

def test_get_model_list_env(endpoint, env_endpoint, resp, model):  # env_endpoint should be before model
    """Test that the model list is returned correctly."""
    res = model.get_model_list()

    assert isinstance(res, list)
    res = resp.pop()
    assert res._args[0] == 'GET'
    assert res._args[1] == endpoint + '/tags'

    assert len(resp) == 0

@pytest.mark.parametrize('mock_request', [{'status_code': [400]}], indirect=True)
def test_load_fail_stauts(model):
    """Test request failure in model loading."""
    with pytest.raises(requests.RequestException, match=r'^Failed to make request to ollama.*'):
        model.load()

# @pytest.mark.parametrize('mock_request', [{'status_code': 400}], indirect=True)
def test_load_fail_load_pull(model):
    """Test ollama failure in model loading."""
    with pytest.raises(requests.RequestException, match=r'^Failed to download model.*'):
        model.load()

@pytest.mark.parametrize(
        'mock_request', [{
            'content': [
                b'{}',
                b'{ "status": "success" }',
                b'{ "version": "0.0.0" }',
                b'{ "status": "error" }',
                ]
            }],
        indirect=True
    )
def test_load_fail_load_create(model):
    """Test ollama failure in model loading."""
    with pytest.raises(requests.RequestException, match=r'^Failed to create custom model.*'):
        model.load()

@pytest.mark.parametrize(
        'mock_request', [{
            'content': [
                b'{}',
                b'{ "status": "success" }',
                b'{ "version": "0.0.0" }',
                b'{ "status": "success" }',
                ]
            }],
        indirect=True
    )
def test_load_not_present_old_vers(resp, model_base_name, model_name, model):
    """Test successful model loading."""
    model.load()

    res = resp.pop()
    assert res._args[0] == 'POST'
    assert res._args[1] == octo_plugin.DEFAULT_OLLAMA_ENDPOINT + '/create'
    assert res._kwargs['json']['name'] == model_name
    assert res._kwargs['json']['stream'] is False
    assert 'modelfile' in res._kwargs['json']

    res = resp.pop()
    assert res._args[0] == 'GET'

    res = resp.pop()
    assert res._args[0] == 'POST'
    assert res._args[1] == octo_plugin.DEFAULT_OLLAMA_ENDPOINT + '/pull'
    assert res._kwargs['json']['name'] == model_base_name
    assert res._kwargs['json']['stream'] is False

    assert len(resp) == 1  # From get_model_list

@pytest.mark.parametrize(
        'mock_request', [{
            'content': [
                b'{}',
                b'{ "status": "success" }',
                b'{ "version": "1.0.0" }',
                b'{ "status": "success" }',
                ]
            }],
        indirect=True
    )
def test_load_not_present_new_vers(resp, model_base_name, model_name, model):
    """Test successful model loading."""
    model.load()

    res = resp.pop()
    assert res._args[0] == 'POST'
    assert res._args[1] == octo_plugin.DEFAULT_OLLAMA_ENDPOINT + '/create'
    assert res._kwargs['json']['name'] == model_name
    assert res._kwargs['json']['stream'] is False
    assert 'from' in res._kwargs['json']
    assert 'system' in res._kwargs['json']

    res = resp.pop()
    assert res._args[0] == 'GET'

    res = resp.pop()
    assert res._args[0] == 'POST'
    assert res._args[1] == octo_plugin.DEFAULT_OLLAMA_ENDPOINT + '/pull'
    assert res._kwargs['json']['name'] == model_base_name
    assert res._kwargs['json']['stream'] is False

    assert len(resp) == 1  # From get_model_list

@pytest.mark.parametrize(
        'mock_request', [{
            'content': [
                b'{"models": [{"name": "oct_ollama_llama3:8b"}]}',
                ]
            }],
        indirect=True
    )
def test_load_present(resp, model):
    """Test successful model loading."""
    model.load()

    res = resp.pop()
    assert res._args[0] == 'GET'
    assert res._args[1] == octo_plugin.DEFAULT_OLLAMA_ENDPOINT + '/tags'

    assert len(resp) == 0

def test_unload(model):
    """Test that the model is unloaded correctly."""
    model = octo_plugin.OllamaTSLModel()
    model.unload()

def test_translate_token_not_list(model):
    """Test raise for translate calls not finished."""
    tokens = '123'
    src = 'japanese'
    dst = 'english'

    with pytest.raises(TypeError, match=r'tokens must be a list of strings or a list of list of strings'):
        model._translate(tokens, src, dst)

@pytest.mark.parametrize(
    'mock_request', [{
        'content': [
            b'{"done": false, "response": "123"}',
        ]
    }],
    indirect=True
)
def test_translate_not_done(model):
    """Test raise for translate calls not finished."""
    tokens = ['tok1', 'tok2']
    src = 'japanese'
    dst = 'english'

    with pytest.raises(requests.RequestException, match=r'^Failed to translate text with model.*'):
        model._translate(tokens, src, dst)

@pytest.mark.parametrize(
    'mock_request', [{
        'content': [
            b'{"done": "true", "response": "123"}',
        ]
    }],
    indirect=True
)
def test_translate_nonbatch(resp, model):
    """Test that translate calls the translator correctly."""
    tokens = ['tok1', 'tok2']
    src = 'japanese'
    dst = 'english'
    expected = '123'

    res = model._translate(tokens, src, dst)
    assert res == expected

    res = resp.pop()
    assert res._args[0] == 'POST'
    assert res._args[1] == octo_plugin.DEFAULT_OLLAMA_ENDPOINT + '/generate'
    prompt = res._kwargs['json']['prompt']
    assert f'src="{src}"' in prompt
    assert f'dst="{dst}"' in prompt
    inp_text = '. '.join(tokens)
    assert f'text="{inp_text}' in prompt

    assert len(resp) == 0

@pytest.mark.parametrize(
    'mock_request', [{
        'content': [
            b'{"done": "true", "response": "123"}',
            b'{"done": "true", "response": "ABC"}',
        ]
    }],
    indirect=True
)
def test_translate_batch(resp, model):
    """Test that translate calls the translator correctly."""
    model = octo_plugin.OllamaTSLModel()

    tokens = [['tok1', 'tok2'], ['tok3', 'tok4']]
    src = 'japanese'
    dst = 'english'
    expected = ['123', 'ABC']

    res = model._translate(tokens, src, dst)
    assert res == expected

    for tok in tokens[::-1]:
        res = resp.pop()
        assert res._args[0] == 'POST'
        assert res._args[1] == octo_plugin.DEFAULT_OLLAMA_ENDPOINT + '/generate'
        prompt = res._kwargs['json']['prompt']
        assert f'src="{src}"' in prompt
        assert f'dst="{dst}"' in prompt
        inp_text = '. '.join(tok)
        assert f'text="{inp_text}' in prompt

    assert len(resp) == 0
