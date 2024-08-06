###################################################################################
# ocr_translate_ollama - a plugin for ocr_translate              #
# Copyright (C) 2023-present Crivella                                      #
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

from ocr_translate import models as m

class ollamaTSLModel(m.TSLModel):
    """TSLModel plugin to allow usage of ... for translation."""
    class Meta:
        proxy = True

    def load(self):
        """Load the model into memory."""
        # Do something here to load the model or nothing if not needed (should still be defined)

    def unload(self) -> None:
        """Unload the model from memory."""
        # Do something here to unload the model or nothing if not needed (should still be defined)


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
        # Redefine this method with the same signature as above
        # Should return a sring with the translated text.
        # IMPORTANT: the main codebase treats this function as batchable:
        # The input `tokens` can be a list of strings or a list of list of strings. The output should match the input being a string or list of strings.
        # (This is used to leverage the capability of pytorch to batch inputs and outputs for faster performances, or it can also used to write a plugin for an online service by using a single request for multiple inputs using some separator that the service will leave unaltered.)
