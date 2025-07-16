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

__version__ = '0.2.0'

from .commons import MODEL_NAME_PREFIX

tsl_model_data = {
    # Name of the model that will be created in the user database and displayed in the extension
    'name': f'{MODEL_NAME_PREFIX}_llama3:8b',
    # List of ISO 639-1 codes of the source languages that will be supported by the model
    'lang_src': [
        'en', 'it', 'ja', 'zh', 'zht', 'es', 'fr', 'de', 'pt', 'nl', 'ru', 'ko'
    ],
    # List of ISO 639-1 codes of the destination languages that will be supported by the model
    'lang_dst': [
        'en', 'it', 'ja', 'zh', 'zht', 'es', 'fr', 'de', 'pt', 'nl', 'ru', 'ko'
    ],
    # How the model requires the codes to be passed (one of 'iso1', 'iso2b', 'iso2t', 'iso3')
    # If the models codes only partially match or are totally different from one of the ISO standards, see iso1_map
    'lang_code': 'iso1',
    # Name of the entrypoint for the model (should match what is used in pyproject.toml)
    'entrypoint': 'ollama.tsl',
    # Maps ISO-639-1 codes to the codes used by the model. Does not need to map every language, only those that are
    # different from getattr(lang: m.Language, lang_code)
    'iso1_map': {
        'en': 'english',
        'it': 'italian',
        'ja': 'japanese',
        'zh': 'chinese',
        'zht': 'chinese_traditional',
        'es': 'spanish',
        'fr': 'french',
        'de': 'german',
        'pt': 'portuguese',
        'nl': 'dutch',
        'ru': 'russian',
        'ko': 'korean'
    },
    'default_options': {'ignore_chars': '', 'break_chars': ''},
}
