import os
import pickle

import openai


class Open_AI:
    def __init__(self, api_key):
        """
        Start an instance of the OpenAI GPT-3 API.
        """
        self.api_key = api_key
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to the database.
        """
        self.openai = openai
        self.openai.api_key = self.api_key

    def __is_picklable__(self, obj: any) -> bool:
        """
        Internal function to determine if the object is pickable.
        :param obj: The object to check.
        :return: True or False
        """
        try:
            pickle.dumps(obj)
            return True
        except Exception as e:
            return False

    def __getstate__(self):
        """
        Internal function for serialization
        """
        state = self.__dict__.copy()
        for key, val in state.items():
            if not self.__is_picklable__(val):
                state[key] = str(val)
        return state

    def __setstate__(self, state):
        """
        Internal function for deserialization
        :param state: The state to set to the 'self' object of the class
        """
        self.__dict__.update(state)
        self.__connect__()

    def openai_complete(self, prompt, max_tokens=2049, temperature=0.9, top_p=1, frequency_penalty=0, presence_penalty=0, model="text-davinci-003"):
        """
        OpenAI GPT-3 completion API
        :param prompt: The prompt to complete
        :param max_tokens: The maximum number of tokens to generate. Defaults to 100.
        :param temperature: The value used to module the next token probabilities. Defaults to 0.9.
        :param top_p: The cumulative probability for top-p filtering. Defaults to 1.
        :param frequency_penalty: The probability penalty for repeated tokens. Defaults to 0.
        :param presence_penalty: The probability penalty for tokens already in the prompt. Defaults to 0.
        :param model: The model to use for completion. Defaults to "text-davinci-003".
        :return: The completion
        """
        if max_tokens == 2049:
            max_tokens = 2049 - len(prompt)
        response = openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        return response.choices[0].text
