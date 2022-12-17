import json
import os
import pickle
import shutil
import subprocess
import sys

import BPMN_RPA.Scripts.SQLserver as SQLserver
import spacy
import tensorflow

# The BPMN-RPA TextMining module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The BPMN-RPA TextMining module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The TextMining module is based on the Spacy library. Spacy is licensed under the MIT license:
# Copyright (C) 2016-2022 ExplosionAI GmbH, 2016 spaCy GmbH, 2015 Matthew Honnibal
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
# THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

#check if the attribute is present
hasattr(tensorflow, '__version__')

#if the attribute is not present
if not hasattr(tensorflow, '__version__'):
    #add the attribute
    tensorflow.__version__ = sys.version


class TextMining:

    def __init__(self, standard_model='en_core_web_lg'):
        """
        Initializes the TextMining module.
        :param standard_model: The standard model to use. Default is 'en_core_web_lg'. To download this model, see https://spacy.io/models/en. If you want to use any other language, please refer to https://spacy.io/models
        """
        self.standard_model = standard_model
        self.nlp = None
        self.__connect__()

    def __connect__(self):
        """
        Internal function to connect to the Spacy model.
        """
        self.nlp = spacy.load(self.standard_model)

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

    def get_named_entities(self, text):
        """
        Returns the named entities of a text.
        :param text: Text to analyze
        :return: A list of named entities
        """
        doc = self.nlp(text)
        return doc.ents

    def get_named_entities_as_string(self, text):
        """
        Returns the named entities of a text as a string.
        :param text: Text to analyze
        :return: A string of named entities
        """
        doc = self.nlp(text)
        return str(doc.ents)

    def get_named_entities_as_json(self, text):
        """
        Returns the named entities of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of named entities
        """
        doc = self.nlp(text)
        return json.dumps(doc.ents)

    def get_named_entities_as_dict(self, text):
        """
        Returns the named entities of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of named entities
        """
        doc = self.nlp(text)
        return doc.ents

    def get_named_entities_as_list(self, text):
        """
        Returns the named entities of a text as a list.
        :param text: Text to analyze
        :return: A list of named entities
        """
        doc = self.nlp(text)
        return list(doc.ents)

    def get_subjects(self, text):
        """
        Returns the subjects of a text.
        :param text: Text to analyze
        :return: A list of subjects
        """
        doc = self.nlp(text)
        return [chunk.root.text for chunk in doc.noun_chunks if chunk.root.dep_ == "nsubj"]

    def get_subjects_as_string(self, text):
        """
        Returns the subjects of a text as a string.
        :param text: Text to analyze
        :return: A string of subjects
        """
        doc = self.nlp(text)
        return str([chunk.root.text for chunk in doc.noun_chunks if chunk.root.dep_ == "nsubj"])

    def get_subjects_as_json(self, text):
        """
        Returns the subjects of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of subjects
        """
        doc = self.nlp(text)
        return json.dumps([chunk.root.text for chunk in doc.noun_chunks if chunk.root.dep_ == "nsubj"])

    def get_subjects_as_dict(self, text):
        """
        Returns the subjects of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of subjects
        """
        doc = self.nlp(text)
        return [chunk.root.text for chunk in doc.noun_chunks if chunk.root.dep_ == "nsubj"]

    def get_subjects_as_list(self, text):
        """
        Returns the subjects of a text as a list.
        :param text: Text to analyze
        :return: A list of subjects
        """
        doc = self.nlp(text)
        return [chunk.root.text for chunk in doc.noun_chunks if chunk.root.dep_ == "nsubj"]

    def get_verbs(self, text):
        """
        Returns the verbs of a text.
        :param text: Text to analyze
        :return: A list of verbs
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "VERB"]

    def get_verbs_as_string(self, text):
        """
        Returns the verbs of a text as a string.
        :param text: Text to analyze
        :return: A string of verbs
        """
        doc = self.nlp(text)
        return str([token.text for token in doc if token.pos_ == "VERB"])

    def get_verbs_as_json(self, text):
        """
        Returns the verbs of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of verbs
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc if token.pos_ == "VERB"])

    def get_verbs_as_dict(self, text):
        """
        Returns the verbs of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of verbs
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "VERB"]

    def get_verbs_as_list(self, text):
        """
        Returns the verbs of a text as a list.
        :param text: Text to analyze
        :return: A list of verbs
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "VERB"]

    def get_nouns(self, text):
        """
        Returns the nouns of a text.
        :param text: Text to analyze
        :return: A list of nouns
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "NOUN"]

    def get_nouns_as_string(self, text):
        """
        Returns the nouns of a text as a string.
        :param text: Text to analyze
        :return: A string of nouns
        """
        doc = self.nlp(text)
        return str([token.text for token in doc if token.pos_ == "NOUN"])

    def get_nouns_as_json(self, text):
        """
        Returns the nouns of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of nouns
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc if token.pos_ == "NOUN"])

    def get_nouns_as_dict(self, text):
        """
        Returns the nouns of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of nouns
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "NOUN"]

    def get_nouns_as_list(self, text):
        """
        Returns the nouns of a text as a list.
        :param text: Text to analyze
        :return: A list of nouns
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "NOUN"]

    def get_adjectives(self, text):
        """
        Returns the adjectives of a text.
        :param text: Text to analyze
        :return: A list of adjectives
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "ADJ"]

    def get_adjectives_as_string(self, text):
        """
        Returns the adjectives of a text as a string.
        :param text: Text to analyze
        :return: A string of adjectives
        """
        doc = self.nlp(text)
        return str([token.text for token in doc if token.pos_ == "ADJ"])

    def get_adjectives_as_json(self, text):
        """
        Returns the adjectives of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of adjectives
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc if token.pos_ == "ADJ"])

    def get_adjectives_as_dict(self, text):
        """
        Returns the adjectives of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of adjectives
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "ADJ"]

    def get_adjectives_as_list(self, text):
        """
        Returns the adjectives of a text as a list.
        :param text: Text to analyze
        :return: A list of adjectives
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "ADJ"]

    def get_adverbs(self, text):
        """
        Returns the adverbs of a text.
        :param text: Text to analyze
        :return: A list of adverbs
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "ADV"]

    def get_adverbs_as_string(self, text):
        """
        Returns the adverbs of a text as a string.
        :param text: Text to analyze
        :return: A string of adverbs
        """
        doc = self.nlp(text)
        return str([token.text for token in doc if token.pos_ == "ADV"])

    def get_adverbs_as_json(self, text):
        """
        Returns the adverbs of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of adverbs
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc if token.pos_ == "ADV"])

    def get_adverbs_as_dict(self, text):
        """
        Returns the adverbs of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of adverbs
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "ADV"]

    def get_adverbs_as_list(self, text):
        """
        Returns the adverbs of a text as a list.
        :param text: Text to analyze
        :return: A list of adverbs
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.pos_ == "ADV"]

    def get_persons(self, text):
        """
        Returns the persons of a text.
        :param text: Text to analyze
        :return: A list of persons
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "PERSON"]

    def get_persons_as_string(self, text):
        """
        Returns the persons of a text as a string.
        :param text: Text to analyze
        :return: A string of persons
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "PERSON"])

    def get_persons_as_json(self, text):
        """
        Returns the persons of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of persons
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "PERSON"])

    def get_persons_as_dict(self, text):
        """
        Returns the persons of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of persons
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "PERSON"]

    def get_persons_as_list(self, text):
        """
        Returns the persons of a text as a list.
        :param text: Text to analyze
        :return: A list of persons
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "PERSON"]

    def get_locations(self, text):
        """
        Returns the locations of a text.
        :param text: Text to analyze
        :return: A list of locations
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "LOC"]

    def get_locations_as_string(self, text):
        """
        Returns the locations of a text as a string.
        :param text: Text to analyze
        :return: A string of locations
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "LOC"])

    def get_locations_as_json(self, text):
        """
        Returns the locations of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of locations
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "LOC"])

    def get_locations_as_dict(self, text):
        """
        Returns the locations of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of locations
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "LOC"]

    def get_locations_as_list(self, text):
        """
        Returns the locations of a text as a list.
        :param text: Text to analyze
        :return: A list of locations
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "LOC"]

    def get_organizations(self, text):
        """
        Returns the organizations of a text.
        :param text: Text to analyze
        :return: A list of organizations
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "ORG"]

    def get_organizations_as_string(self, text):
        """
        Returns the organizations of a text as a string.
        :param text: Text to analyze
        :return: A string of organizations
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "ORG"])

    def get_organizations_as_json(self, text):
        """
        Returns the organizations of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of organizations
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "ORG"])

    def get_organizations_as_dict(self, text):
        """
        Returns the organizations of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of organizations
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "ORG"]

    def get_organizations_as_list(self, text):
        """
        Returns the organizations of a text as a list.
        :param text: Text to analyze
        :return: A list of organizations
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "ORG"]

    def get_dates(self, text):
        """
        Returns the dates of a text.
        :param text: Text to analyze
        :return: A list of dates
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "DATE"]

    def get_dates_as_string(self, text):
        """
        Returns the dates of a text as a string.
        :param text: Text to analyze
        :return: A string of dates
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "DATE"])

    def get_dates_as_json(self, text):
        """
        Returns the dates of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of dates
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "DATE"])

    def get_dates_as_dict(self, text):
        """
        Returns the dates of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of dates
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "DATE"]

    def get_dates_as_list(self, text):
        """
        Returns the dates of a text as a list.
        :param text: Text to analyze
        :return: A list of dates
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "DATE"]

    def get_money(self, text):
        """
        Returns the money of a text.
        :param text: Text to analyze
        :return: A list of money
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "MONEY"]

    def get_money_as_string(self, text):
        """
        Returns the money of a text as a string.
        :param text: Text to analyze
        :return: A string of money
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "MONEY"])

    def get_money_as_json(self, text):
        """
        Returns the money of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of money
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "MONEY"])

    def get_money_as_dict(self, text):
        """
        Returns the money of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of money
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "MONEY"]

    def get_money_as_list(self, text):
        """
        Returns the money of a text as a list.
        :param text: Text to analyze
        :return: A list of money
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "MONEY"]

    def get_percentages(self, text):
        """
        Returns the percentages of a text.
        :param text: Text to analyze
        :return: A list of percentages
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "PERCENT"]

    def get_percentages_as_string(self, text):
        """
        Returns the percentages of a text as a string.
        :param text: Text to analyze
        :return: A string of percentages
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "PERCENT"])

    def get_percentages_as_json(self, text):
        """
        Returns the percentages of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of percentages
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "PERCENT"])

    def get_percentages_as_dict(self, text):
        """
        Returns the percentages of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of percentages
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "PERCENT"]

    def get_percentages_as_list(self, text):
        """
        Returns the percentages of a text as a list.
        :param text: Text to analyze
        :return: A list of percentages
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "PERCENT"]

    def get_times(self, text):
        """
        Returns the times of a text.
        :param text: Text to analyze
        :return: A list of times
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "TIME"]

    def get_times_as_string(self, text):
        """
        Returns the times of a text as a string.
        :param text: Text to analyze
        :return: A string of times
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "TIME"])

    def get_times_as_json(self, text):
        """
        Returns the times of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of times
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "TIME"])

    def get_times_as_dict(self, text):
        """
        Returns the times of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of times
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "TIME"]

    def get_times_as_list(self, text):
        """
        Returns the times of a text as a list.
        :param text: Text to analyze
        :return: A list of times
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "TIME"]

    def get_nationalities(self, text):
        """
        Returns the nationalities of a text.
        :param text: Text to analyze
        :return: A list of nationalities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "NORP"]

    def get_nationalities_as_string(self, text):
        """
        Returns the nationalities of a text as a string.
        :param text: Text to analyze
        :return: A string of nationalities
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "NORP"])

    def get_nationalities_as_json(self, text):
        """
        Returns the nationalities of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of nationalities
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "NORP"])

    def get_nationalities_as_dict(self, text):
        """
        Returns the nationalities of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of nationalities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "NORP"]

    def get_nationalities_as_list(self, text):
        """
        Returns the nationalities of a text as a list.
        :param text: Text to analyze
        :return: A list of nationalities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "NORP"]

    def get_languages(self, text):
        """
        Returns the languages of a text.
        :param text: Text to analyze
        :return: A list of languages
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "LANGUAGE"]

    def get_languages_as_string(self, text):
        """
        Returns the languages of a text as a string.
        :param text: Text to analyze
        :return: A string of languages
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "LANGUAGE"])

    def get_languages_as_json(self, text):
        """
        Returns the languages of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of languages
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "LANGUAGE"])

    def get_languages_as_dict(self, text):
        """
        Returns the languages of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of languages
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "LANGUAGE"]

    def get_languages_as_list(self, text):
        """
        Returns the languages of a text as a list.
        :param text: Text to analyze
        :return: A list of languages
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "LANGUAGE"]

    def get_facilities(self, text):
        """
        Returns the facilities of a text.
        :param text: Text to analyze
        :return: A list of facilities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "FAC"]

    def get_facilities_as_string(self, text):
        """
        Returns the facilities of a text as a string.
        :param text: Text to analyze
        :return: A string of facilities
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "FAC"])

    def get_facilities_as_json(self, text):
        """
        Returns the facilities of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of facilities
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "FAC"])

    def get_facilities_as_dict(self, text):
        """
        Returns the facilities of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of facilities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "FAC"]

    def get_facilities_as_list(self, text):
        """
        Returns the facilities of a text as a list.
        :param text: Text to analyze
        :return: A list of facilities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "FAC"]

    def get_cities_countries_and_states(self, text):
        """
        Returns the cities of a text.
        :param text: Text to analyze
        :return: A list of cities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "GPE"]

    def get_cities_countries_and_states_as_string(self, text):
        """
        Returns the cities of a text as a string.
        :param text: Text to analyze
        :return: A string of cities
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "GPE"])

    def get_cities_countries_and_states_as_json(self, text):
        """
        Returns the cities of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of cities
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "GPE"])

    def get_cities_countries_and_states_as_dict(self, text):
        """
        Returns the cities of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of cities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "GPE"]

    def get_cities_countries_and_states_as_list(self, text):
        """
        Returns the cities of a text as a list.
        :param text: Text to analyze
        :return: A list of cities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "GPE"]

    def get_products(self, text):
        """
        Returns the products of a text.
        :param text: Text to analyze
        :return: A list of products
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "PRODUCT"]

    def get_products_as_string(self, text):
        """
        Returns the products of a text as a string.
        :param text: Text to analyze
        :return: A string of products
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "PRODUCT"])

    def get_products_as_json(self, text):
        """
        Returns the products of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of products
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "PRODUCT"])

    def get_products_as_dict(self, text):
        """
        Returns the products of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of products
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "PRODUCT"]

    def get_products_as_list(self, text):
        """
        Returns the products of a text as a list.
        :param text: Text to analyze
        :return: A list of products
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "PRODUCT"]

    def get_laws(self, text):
        """
        Returns the laws of a text.
        :param text: Text to analyze
        :return: A list of laws
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "LAW"]

    def get_laws_as_string(self, text):
        """
        Returns the laws of a text as a string.
        :param text: Text to analyze
        :return: A string of laws
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "LAW"])

    def get_laws_as_json(self, text):
        """
        Returns the laws of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of laws
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "LAW"])

    def get_laws_as_dict(self, text):
        """
        Returns the laws of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of laws
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "LAW"]

    def get_laws_as_list(self, text):
        """
        Returns the laws of a text as a list.
        :param text: Text to analyze
        :return: A list of laws
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "LAW"]

    def get_quantities(self, text):
        """
        Returns the quantities of a text.
        :param text: Text to analyze
        :return: A list of quantities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "QUANTITY"]

    def get_quantities_as_string(self, text):
        """
        Returns the quantities of a text as a string.
        :param text: Text to analyze
        :return: A string of quantities
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "QUANTITY"])

    def get_quantities_as_json(self, text):
        """
        Returns the quantities of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of quantities
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "QUANTITY"])

    def get_quantities_as_dict(self, text):
        """
        Returns the quantities of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of quantities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "QUANTITY"]

    def get_quantities_as_list(self, text):
        """
        Returns the quantities of a text as a list.
        :param text: Text to analyze
        :return: A list of quantities
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "QUANTITY"]

    def get_ordinal_numbers(self, text):
        """
        Returns the ordinal numbers of a text.
        :param text: Text to analyze
        :return: A list of ordinal numbers
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "ORDINAL"]

    def get_ordinal_numbers_as_string(self, text):
        """
        Returns the ordinal numbers of a text as a string.
        :param text: Text to analyze
        :return: A string of ordinal numbers
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "ORDINAL"])

    def get_ordinal_numbers_as_json(self, text):
        """
        Returns the ordinal numbers of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of ordinal numbers
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "ORDINAL"])

    def get_ordinal_numbers_as_dict(self, text):
        """
        Returns the ordinal numbers of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of ordinal numbers
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "ORDINAL"]

    def get_ordinal_numbers_as_list(self, text):
        """
        Returns the ordinal numbers of a text as a list.
        :param text: Text to analyze
        :return: A list of ordinal numbers
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "ORDINAL"]

    def get_cardinal_numbers(self, text):
        """
        Returns the cardinal numbers of a text.
        :param text: Text to analyze
        :return: A list of cardinal numbers
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "CARDINAL"]

    def get_cardinal_numbers_as_string(self, text):
        """
        Returns the cardinal numbers of a text as a string.
        :param text: Text to analyze
        :return: A string of cardinal numbers
        """
        doc = self.nlp(text)
        return str([token.text for token in doc.ents if token.label_ == "CARDINAL"])

    def get_cardinal_numbers_as_json(self, text):
        """
        Returns the cardinal numbers of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of cardinal numbers
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc.ents if token.label_ == "CARDINAL"])

    def get_cardinal_numbers_as_dict(self, text):
        """
        Returns the cardinal numbers of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of cardinal numbers
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "CARDINAL"]

    def get_cardinal_numbers_as_list(self, text):
        """
        Returns the cardinal numbers of a text as a list.
        :param text: Text to analyze
        :return: A list of cardinal numbers
        """
        doc = self.nlp(text)
        return [token.text for token in doc.ents if token.label_ == "CARDINAL"]

    def get_part_of_speech_tags(self, text):
        """
        Returns the part of speech tags of a text.
        :param text: Text to analyze
        :return: A list of part of speech tags
        """
        doc = self.nlp(text)
        return [token.pos_ for token in doc]

    def get_part_of_speech_tags_as_string(self, text):
        """
        Returns the part of speech tags of a text as a string.
        :param text: Text to analyze
        :return: A string of part of speech tags
        """
        doc = self.nlp(text)
        return str([token.pos_ for token in doc])

    def get_part_of_speech_tags_as_json(self, text):
        """
        Returns the part of speech tags of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of part of speech tags
        """
        doc = self.nlp(text)
        return json.dumps([token.pos_ for token in doc])

    def get_part_of_speech_tags_as_dict(self, text):
        """
        Returns the part of speech tags of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of part of speech tags
        """
        doc = self.nlp(text)
        return [token.pos_ for token in doc]

    def get_part_of_speech_tags_as_list(self, text):
        """
        Returns the part of speech tags of a text as a list.
        :param text: Text to analyze
        :return: A list of part of speech tags
        """
        doc = self.nlp(text)
        return [token.pos_ for token in doc]

    def get_lemmas(self, text):
        """
        Returns the lemmas of a text.
        :param text: Text to analyze
        :return: A list of lemmas
        """
        doc = self.nlp(text)
        return [token.lemma_ for token in doc]

    def get_lemmas_as_string(self, text):
        """
        Returns the lemmas of a text as a string.
        :param text: Text to analyze
        :return: A string of lemmas
        """
        doc = self.nlp(text)
        return str([token.lemma_ for token in doc])

    def get_lemmas_as_json(self, text):
        """
        Returns the lemmas of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of lemmas
        """
        doc = self.nlp(text)
        return json.dumps([token.lemma_ for token in doc])

    def get_lemmas_as_dict(self, text):
        """
        Returns the lemmas of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of lemmas
        """
        doc = self.nlp(text)
        return [token.lemma_ for token in doc]

    def get_lemmas_as_list(self, text):
        """
        Returns the lemmas of a text as a list.
        :param text: Text to analyze
        :return: A list of lemmas
        """
        doc = self.nlp(text)
        return [token.lemma_ for token in doc]

    def get_dependencies(self, text):
        """
        Returns the dependencies of a text.
        :param text: Text to analyze
        :return: A list of dependencies
        """
        doc = self.nlp(text)
        return [token.dep_ for token in doc]

    def get_dependencies_as_string(self, text):
        """
        Returns the dependencies of a text as a string.
        :param text: Text to analyze
        :return: A string of dependencies
        """
        doc = self.nlp(text)
        return str([token.dep_ for token in doc])

    def get_dependencies_as_json(self, text):
        """
        Returns the dependencies of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of dependencies
        """
        doc = self.nlp(text)
        return json.dumps([token.dep_ for token in doc])

    def get_dependencies_as_dict(self, text):
        """
        Returns the dependencies of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of dependencies
        """
        doc = self.nlp(text)
        return [token.dep_ for token in doc]

    def get_dependencies_as_list(self, text):
        """
        Returns the dependencies of a text as a list.
        :param text: Text to analyze
        :return: A list of dependencies
        """
        doc = self.nlp(text)
        return [token.dep_ for token in doc]

    def sentiment_analysis(self, text):
        """
        Returns the sentiment analysis of a text.
        :param text: Text to analyze
        :return: A list of sentiment analysis
        """
        doc = self.nlp(text)
        return doc.sentiment

    def sentiment_analysis_as_string(self, text):
        """
        Returns the sentiment analysis of a text as a string.
        :param text: Text to analyze
        :return: A string of sentiment analysis
        """
        doc = self.nlp(text)
        return str(doc.sentiment)

    def sentiment_analysis_as_json(self, text):
        """
        Returns the sentiment analysis of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of sentiment analysis
        """
        doc = self.nlp(text)
        return json.dumps(doc.sentiment)

    def sentiment_analysis_as_dict(self, text):
        """
        Returns the sentiment analysis of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of sentiment analysis
        """
        doc = self.nlp(text)
        return doc.sentiment

    def sentiment_analysis_as_list(self, text):
        """
        Returns the sentiment analysis of a text as a list.
        :param text: Text to analyze
        :return: A list of sentiment analysis
        """
        doc = self.nlp(text)
        return doc.sentiment

    def get_noun_chunks(self, text):
        """
        Returns the noun chunks of a text.
        :param text: Text to analyze
        :return: A list of noun chunks
        """
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

    def get_noun_chunks_as_string(self, text):
        """
        Returns the noun chunks of a text as a string.
        :param text: Text to analyze
        :return: A string of noun chunks
        """
        doc = self.nlp(text)
        return str([chunk.text for chunk in doc.noun_chunks])

    def get_noun_chunks_as_json(self, text):
        """
        Returns the noun chunks of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of noun chunks
        """
        doc = self.nlp(text)
        return json.dumps([chunk.text for chunk in doc.noun_chunks])

    def get_noun_chunks_as_dict(self, text):
        """
        Returns the noun chunks of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of noun chunks
        """
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

    def get_noun_chunks_as_list(self, text):
        """
        Returns the noun chunks of a text as a list.
        :param text: Text to analyze
        :return: A list of noun chunks
        """
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

    def get_most_similar_words(self, text):
        """
        Returns the most similar words of a text.
        :param text: Text to analyze
        :return: A list of most similar words
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.has_vector and token.is_oov]

    def get_most_similar_words_as_string(self, text):
        """
        Returns the most similar words of a text as a string.
        :param text: Text to analyze
        :return: A string of most similar words
        """
        doc = self.nlp(text)
        return str([token.text for token in doc if token.has_vector and token.is_oov])

    def get_most_similar_words_as_json(self, text):
        """
        Returns the most similar words of a text as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of most similar words
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc if token.has_vector and token.is_oov])

    def get_most_similar_words_as_dict(self, text):
        """
        Returns the most similar words of a text as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of most similar words
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.has_vector and token.is_oov]

    def get_most_similar_words_as_list(self, text):
        """
        Returns the most similar words of a text as a list.
        :param text: Text to analyze
        :return: A list of most similar words
        """
        doc = self.nlp(text)
        return [token.text for token in doc if token.has_vector and token.is_oov]

    def get_most_similar_words_with_similarity(self, text):
        """
        Returns the most similar words of a text with similarity.
        :param text: Text to analyze
        :return: A list of most similar words with similarity
        """
        doc = self.nlp(text)
        return [(token.text, token.similarity(doc)) for token in doc if token.has_vector and token.is_oov]

    def get_most_similar_words_with_similarity_as_string(self, text):
        """
        Returns the most similar words of a text with similarity as a string.
        :param text: Text to analyze
        :return: A string of most similar words with similarity
        """
        doc = self.nlp(text)
        return str([(token.text, token.similarity(doc)) for token in doc if token.has_vector and token.is_oov])

    def get_most_similar_words_with_similarity_as_json(self, text):
        """
        Returns the most similar words of a text with similarity as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of most similar words with similarity
        """
        doc = self.nlp(text)
        return json.dumps([(token.text, token.similarity(doc)) for token in doc if token.has_vector and token.is_oov])

    def get_most_similar_words_with_similarity_as_dict(self, text):
        """
        Returns the most similar words of a text with similarity as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of most similar words with similarity
        """
        doc = self.nlp(text)
        return [(token.text, token.similarity(doc)) for token in doc if token.has_vector and token.is_oov]

    def get_most_similar_words_with_similarity_as_list(self, text):
        """
        Returns the most similar words of a text with similarity as a list.
        :param text: Text to analyze
        :return: A list of most similar words with similarity
        """
        doc = self.nlp(text)
        return [(token.text, token.similarity(doc)) for token in doc if token.has_vector and token.is_oov]

    def get_best_match(self, text, words):
        """
        Returns the best match of a text.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A list of best match
        """
        doc = self.nlp(text)
        return [doc.similarity(self.nlp(word)) for word in words]

    def get_best_match_as_string(self, text, words):
        """
        Returns the best match of a text as a string.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A string of best match
        """
        doc = self.nlp(text)
        return str([doc.similarity(self.nlp(word)) for word in words])

    def get_best_match_as_json(self, text, words):
        """
        Returns the best match of a text as a JSON string.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A JSON string of best match
        """
        doc = self.nlp(text)
        return json.dumps([doc.similarity(self.nlp(word)) for word in words])

    def get_best_match_as_dict(self, text, words):
        """
        Returns the best match of a text as a dictionary.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A dictionary of best match
        """
        doc = self.nlp(text)
        return [doc.similarity(self.nlp(word)) for word in words]

    def get_best_match_as_list(self, text, words):
        """
        Returns the best match of a text as a list.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A list of best match
        """
        doc = self.nlp(text)
        return [doc.similarity(self.nlp(word)) for word in words]

    def get_best_match_with_similarity(self, text, words):
        """
        Returns the best match of a text with similarity.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A list of best match with similarity
        """
        doc = self.nlp(text)
        return [(word, doc.similarity(self.nlp(word))) for word in words]

    def get_best_match_with_similarity_as_string(self, text, words):
        """
        Returns the best match of a text with similarity as a string.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A string of best match with similarity
        """
        doc = self.nlp(text)
        return str([(word, doc.similarity(self.nlp(word))) for word in words])

    def get_best_match_with_similarity_as_json(self, text, words):
        """
        Returns the best match of a text with similarity as a JSON string.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A JSON string of best match with similarity
        """
        doc = self.nlp(text)
        return json.dumps([(word, doc.similarity(self.nlp(word))) for word in words])

    def get_best_match_with_similarity_as_dict(self, text, words):
        """
        Returns the best match of a text with similarity as a dictionary.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A dictionary of best match with similarity
        """
        doc = self.nlp(text)
        return [(word, doc.similarity(self.nlp(word))) for word in words]

    def get_best_match_with_similarity_as_list(self, text, words):
        """
        Returns the best match of a text with similarity as a list.
        :param text: Text to analyze
        :param words: List of words to match
        :return: A list of best match with similarity
        """
        doc = self.nlp(text)
        return [(word, doc.similarity(self.nlp(word))) for word in words]

    def get_summary(self, text):
        """
        Returns the summary of a text.
        :param text: Text to analyze
        :return: A list of summary
        """
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents if sent._.is_highest]

    def get_summary_as_string(self, text, ratio=0.2):
        """
        Returns the summary of a text as a string.
        :param text: Text to analyze
        :param ratio: Ratio of summary
        :return: A string of summary
        """
        doc = self.nlp(text)
        return str([sent.text for sent in doc.sents if sent._.is_highest])

    def get_summary_as_json(self, text, ratio=0.2):
        """
        Returns the summary of a text as a JSON string.
        :param text: Text to analyze
        :param ratio: Ratio of summary
        :return: A JSON string of summary
        """
        doc = self.nlp(text)
        return json.dumps([sent.text for sent in doc.sents if sent._.is_highest])

    def get_summary_as_dict(self, text, ratio=0.2):
        """
        Returns the summary of a text as a dictionary.
        :param text: Text to analyze
        :param ratio: Ratio of summary
        :return: A dictionary of summary
        """
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents if sent._.is_highest]

    def get_summary_as_list(self, text, ratio=0.2):
        """
        Returns the summary of a text as a list.
        :param text: Text to analyze
        :param ratio: Ratio of summary
        :return: A list of summary
        """
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents if sent._.is_highest]

    def get_stopwords(self):
        """
        Returns the list of stopwords.
        :return: A list of stopwords
        """
        return self.nlp.Defaults.stop_words

    def get_stopwords_as_string(self):
        """
        Returns the list of stopwords as a string.
        :return: A string of stopwords
        """
        return str(self.nlp.Defaults.stop_words)

    def get_stopwords_as_json(self):
        """
        Returns the list of stopwords as a JSON string.
        :return: A JSON string of stopwords
        """
        return json.dumps(self.nlp.Defaults.stop_words)

    def get_stopwords_as_dict(self):
        """
        Returns the list of stopwords as a dictionary.
        :return: A dictionary of stopwords
        """
        return self.nlp.Defaults.stop_words

    def get_stopwords_as_list(self):
        """
        Returns the list of stopwords as a list.
        :return: A list of stopwords
        """
        return self.nlp.Defaults.stop_words

    def get_tokens(self, text):
        """
        Returns the list of tokens.
        :param text: Text to analyze
        :return: A list of tokens
        """
        doc = self.nlp(text)
        return [token.text for token in doc]

    def get_tokens_as_string(self, text):
        """
        Returns the list of tokens as a string.
        :param text: Text to analyze
        :return: A string of tokens
        """
        doc = self.nlp(text)
        return str([token.text for token in doc])

    def get_tokens_as_json(self, text):
        """
        Returns the list of tokens as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of tokens
        """
        doc = self.nlp(text)
        return json.dumps([token.text for token in doc])

    def get_tokens_as_dict(self, text):
        """
        Returns the list of tokens as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of tokens
        """
        doc = self.nlp(text)
        return [token.text for token in doc]

    def get_tokens_as_list(self, text):
        """
        Returns the list of tokens as a list.
        :param text: Text to analyze
        :return: A list of tokens
        """
        doc = self.nlp(text)
        return [token.text for token in doc]

    def get_tokens_with_pos(self, text):
        """
        Returns the list of tokens with POS.
        :param text: Text to analyze
        :return: A list of tokens with POS
        """
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def get_tokens_with_pos_as_string(self, text):
        """
        Returns the list of tokens with POS as a string.
        :param text: Text to analyze
        :return: A string of tokens with POS
        """
        doc = self.nlp(text)
        return str([(token.text, token.pos_) for token in doc])

    def get_tokens_with_pos_as_json(self, text):
        """
        Returns the list of tokens with POS as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of tokens with POS
        """
        doc = self.nlp(text)
        return json.dumps([(token.text, token.pos_) for token in doc])

    def get_tokens_with_pos_as_dict(self, text):
        """
        Returns the list of tokens with POS as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of tokens with POS
        """
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def get_tokens_with_pos_as_list(self, text):
        """
        Returns the list of tokens with POS as a list.
        :param text: Text to analyze
        :return: A list of tokens with POS
        """
        doc = self.nlp(text)
        return [(token.text, token.pos_) for token in doc]

    def get_tokens_with_pos_and_dep(self, text):
        """
        Returns the list of tokens with POS and dependency.
        :param text: Text to analyze
        :return: A list of tokens with POS and dependency
        """
        doc = self.nlp(text)
        return [(token.text, token.pos_, token.dep_) for token in doc]

    def get_tokens_with_pos_and_dep_as_string(self, text):
        """
        Returns the list of tokens with POS and dependency as a string.
        :param text: Text to analyze
        :return: A string of tokens with POS and dependency
        """
        doc = self.nlp(text)
        return str([(token.text, token.pos_, token.dep_) for token in doc])

    def get_tokens_with_pos_and_dep_as_json(self, text):
        """
        Returns the list of tokens with POS and dependency as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of tokens with POS and dependency
        """
        doc = self.nlp(text)
        return json.dumps([(token.text, token.pos_, token.dep_) for token in doc])

    def get_tokens_with_pos_and_dep_as_dict(self, text):
        """
        Returns the list of tokens with POS and dependency as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of tokens with POS and dependency
        """
        doc = self.nlp(text)
        return [(token.text, token.pos_, token.dep_) for token in doc]

    def get_tokens_with_pos_and_dep_as_list(self, text):
        """
        Returns the list of tokens with POS and dependency as a list.
        :param text: Text to analyze
        :return: A list of tokens with POS and dependency
        """
        doc = self.nlp(text)
        return [(token.text, token.pos_, token.dep_) for token in doc]

    def get_tokens_with_lemma(self, text):
        """
        Returns the list of tokens with lemma.
        :param text: Text to analyze
        :return: A list of tokens with lemma
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_) for token in doc]

    def get_tokens_with_lemma_as_string(self, text):
        """
        Returns the list of tokens with lemma as a string.
        :param text: Text to analyze
        :return: A string of tokens with lemma
        """
        doc = self.nlp(text)
        return str([(token.text, token.lemma_) for token in doc])

    def get_tokens_with_lemma_as_json(self, text):
        """
        Returns the list of tokens with lemma as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of tokens with lemma
        """
        doc = self.nlp(text)
        return json.dumps([(token.text, token.lemma_) for token in doc])

    def get_tokens_with_lemma_as_dict(self, text):
        """
        Returns the list of tokens with lemma as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of tokens with lemma
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_) for token in doc]

    def get_tokens_with_lemma_as_list(self, text):
        """
        Returns the list of tokens with lemma as a list.
        :param text: Text to analyze
        :return: A list of tokens with lemma
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_) for token in doc]

    def get_tokens_with_lemma_and_pos(self, text):
        """
        Returns the list of tokens with lemma and POS.
        :param text: Text to analyze
        :return: A list of tokens with lemma and POS
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_, token.pos_) for token in doc]

    def get_tokens_with_lemma_and_pos_as_string(self, text):
        """
        Returns the list of tokens with lemma and POS as a string.
        :param text: Text to analyze
        :return: A string of tokens with lemma and POS
        """
        doc = self.nlp(text)
        return str([(token.text, token.lemma_, token.pos_) for token in doc])

    def get_tokens_with_lemma_and_pos_as_json(self, text):
        """
        Returns the list of tokens with lemma and POS as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of tokens with lemma and POS
        """
        doc = self.nlp(text)
        return json.dumps([(token.text, token.lemma_, token.pos_) for token in doc])

    def get_tokens_with_lemma_and_pos_as_dict(self, text):
        """
        Returns the list of tokens with lemma and POS as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of tokens with lemma and POS
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_, token.pos_) for token in doc]

    def get_tokens_with_lemma_and_pos_as_list(self, text):
        """
        Returns the list of tokens with lemma and POS as a list.
        :param text: Text to analyze
        :return: A list of tokens with lemma and POS
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_, token.pos_) for token in doc]

    def get_tokens_with_lemma_and_pos_and_dep(self, text):
        """
        Returns the list of tokens with lemma, POS and dependency.
        :param text: Text to analyze
        :return: A list of tokens with lemma, POS and dependency
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_, token.pos_, token.dep_) for token in doc]

    def get_tokens_with_lemma_and_pos_and_dep_as_string(self, text):
        """
        Returns the list of tokens with lemma, POS and dependency as a string.
        :param text: Text to analyze
        :return: A string of tokens with lemma, POS and dependency
        """
        doc = self.nlp(text)
        return str([(token.text, token.lemma_, token.pos_, token.dep_) for token in doc])

    def get_tokens_with_lemma_and_pos_and_dep_as_json(self, text):
        """
        Returns the list of tokens with lemma, POS and dependency as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of tokens with lemma, POS and dependency
        """
        doc = self.nlp(text)
        return json.dumps([(token.text, token.lemma_, token.pos_, token.dep_) for token in doc])

    def get_tokens_with_lemma_and_pos_and_dep_as_dict(self, text):
        """
        Returns the list of tokens with lemma, POS and dependency as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of tokens with lemma, POS and dependency
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_, token.pos_, token.dep_) for token in doc]

    def get_tokens_with_lemma_and_pos_and_dep_as_list(self, text):
        """
        Returns the list of tokens with lemma, POS and dependency as a list.
        :param text: Text to analyze
        :return: A list of tokens with lemma, POS and dependency
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_, token.pos_, token.dep_) for token in doc]

    def get_tokens_with_lemma_and_pos_and_dep_and_shape(self, text):
        """
        Returns the list of tokens with lemma, POS, dependency and shape.
        :param text: Text to analyze
        :return: A list of tokens with lemma, POS, dependency and shape
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_, token.pos_, token.dep_, token.shape_) for token in doc]

    def get_tokens_with_lemma_and_pos_and_dep_and_shape_as_string(self, text):
        """
        Returns the list of tokens with lemma, POS, dependency and shape as a string.
        :param text: Text to analyze
        :return: A string of tokens with lemma, POS, dependency and shape
        """
        doc = self.nlp(text)
        return str([(token.text, token.lemma_, token.pos_, token.dep_, token.shape_) for token in doc])

    def get_tokens_with_lemma_and_pos_and_dep_and_shape_as_json(self, text):
        """
        Returns the list of tokens with lemma, POS, dependency and shape as a JSON string.
        :param text: Text to analyze
        :return: A JSON string of tokens with lemma, POS, dependency and shape
        """
        doc = self.nlp(text)
        return json.dumps([(token.text, token.lemma_, token.pos_, token.dep_, token.shape_) for token in doc])

    def get_tokens_with_lemma_and_pos_and_dep_and_shape_as_dict(self, text):
        """
        Returns the list of tokens with lemma, POS, dependency and shape as a dictionary.
        :param text: Text to analyze
        :return: A dictionary of tokens with lemma, POS, dependency and shape
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_, token.pos_, token.dep_, token.shape_) for token in doc]

    def get_tokens_with_lemma_and_pos_and_dep_and_shape_as_list(self, text):
        """
        Returns the list of tokens with lemma, POS, dependency and shape as a list.
        :param text: Text to analyze
        :return: A list of tokens with lemma, POS, dependency and shape
        """
        doc = self.nlp(text)
        return [(token.text, token.lemma_, token.pos_, token.dep_, token.shape_) for token in doc]

    def __create_config__(self):
        """
        Fill the base_config.cfg file with remaining defaults and save it as config.cfg.
        After you’ve saved the starter config to a file base_config.cfg, you can use the init fill-config command to fill in the remaining defaults. Training configs should always be complete and without hidden defaults, to keep your experiments reproducible.
        """
        # Check if english model is present
        nlp = None
        try:
            nlp = spacy.load("en_core_web_lg")
        except Exception as e:
            print("English model is not installed. Now downloading and installing...")
            # Download the englisch model
            subprocess.run("python -m spacy download en_core_web_lg", shell=True)
        subprocess.run("python -m spacy init fill-config base_config.cfg config.cfg", shell=True)

    def train(self, data, folder, model_name="model_best", language="en"):
        """
        Train the model with the data from the given database.
        :param data: The data to train the model with
        :param folder: The folder to save the model to.
        :param model_name: The name of the model. Default is "model_best".
        :param language: The language of the data. Default is "en".
        """
        nlp = spacy.blank(language)
        cfglang = ""
        # check if right language is used in config.cfg file
        module_path = os.path.dirname(__file__)
        cfg = module_path + "/config.cfg"
        with open(cfg, "r") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                if line.startswith("lang = "):
                    cfglang = line[7:].replace("\n", "")
                    break
        if cfglang != language:
            # replace the language in the config.cfg file
            with open(cfg, "r") as f:
                lines = f.readlines()
            with open(cfg, "w") as f:
                for line in lines:
                    if line.startswith("lang = "):
                        f.write("lang = \"" + language + "\"\n")
                    else:
                        f.write(line)
        # Get unique labels
        labels = set([x[1] for x in data])
        db = spacy.tokens.DocBin()
        train = []
        dev = []
        all = []
        for text, label in data:
            doc = nlp.make_doc(text)
            # set doc label
            for lbl in labels:
                if lbl == label:
                    doc.cats[lbl] = 1.0
                else:
                    doc.cats[lbl] = 0.0
            all.append(doc)
        # The dev.spacy file should look exactly the same as the train.spacy file, but should contain new examples that the training process hasn't seen before to get a realistic evaluation of the performance of your model.
        from spacy.cli.train import train
        # split the training data to 20% dev data
        if len(all) >= 5:
            train_data, test_data = all[:int(len(all) * 0.2)], all[int(len(all) * 0.2):]
        else:
            train_data, test_data = all, all
        # Create docbin
        train_db = spacy.tokens.DocBin(docs=train_data)
        dev_db = spacy.tokens.DocBin(docs=test_data)
        # Delete files if they exist
        if os.path.exists("./train.spacy"):
            os.remove("./train.spacy")
        if os.path.exists("./dev.spacy"):
            os.remove("./dev.spacy")
        train_db.to_disk("./train.spacy")
        dev_db.to_disk("./dev.spacy")
        train(config_path=cfg, output_path="./output")
        # move the model to the given path
        # delete the folder with the same name as the model_name if it exists
        if os.path.exists(folder + "/" + model_name):
            shutil.rmtree(folder + "/" + model_name)
        source_dir = "./output/model-best"
        shutil.copytree(source_dir, folder + "/" + model_name)

    def load_model(self, model_path):
        """
        Load the model from the given path.
        :param model_path: The path to the model.
        """
        self.nlp = spacy.load(model_path)

    def save_model(self, model_path):
        """
        Save the model to the given path.
        :param model_path: The path to the model.
        """
        self.nlp.to_disk(model_path)

    def __load_data__(self, data_path):
        """
        Load the data from the given path.
        :param data_path: The path to the data.
        """
        self.data = spacy.tokens.DocBin().from_disk(data_path)

    def predict(self, text):
        """
        Predict the label of the given text by using the already loaded model.
        :param text: The text to predict.
        :return: The predicted label.
        """
        doc = self.nlp(text)
        return max(doc.cats)

    def data_to_jsonl(self, data: list, file_path: str):
        """
        Saves the given data to a jsonl file.
        :param data: The data to save.
        :param file_path: The path to the file.
        """
        with open(file_path, "w") as f:
            for item in data:
                f.write(json.dumps(item) + "\n")

    def __get_data_from_database__(self, host, database, table_name):
        """
        Get the data from the sql server database by using a generator with yield.
        :param host: The host of the database.
        :param database: The name of the database.
        :param table_name: The name of the table in the database. This table must have columns named 'text' and 'label'.
        :return: The data from the database.
        """
        sqlserver = SQLserver.SQLserver(host, database)
        results = sqlserver.sqlserver_query_and_get_results("SELECT * FROM " + table_name)
        for result in results:
            yield result.text, result.label

    def train_from_sql_server_database(self, database, table_name, folder, model_name="model_best", host="localhost", language="en"):
        """
        Train the model with the data from the given database.
        :param host: Optional. The host of the database. Default is "localhost".
        :param database: The path to the database.
        :param table_name: The name of the table in the database. This table must have columns named 'text' and 'label'.
        :param folder: The folder to save the model to.
        :param model_name: The name of the model. Default is "model_best".
        :param language: The language of the data. Default is "en".
        """
        nlp = spacy.blank(language)
        cfglang = ""
        # check if right language is used in config.cfg file in the same folder as this module
        module_path = os.path.dirname(__file__)
        cfg = module_path + "./config.cfg"
        with open(cfg, "r") as f:
            print("opened")
            while True:
                line = f.readline()
                if not line:
                    break
                if line.startswith("lang = "):
                    cfglang = line[7:].replace("\n", "")
                    break
        if cfglang != language:
            # replace the language in the config.cfg file
            with open(cfg, "r") as f:
                lines = f.readlines()
            with open(cfg, "w") as f:
                for line in lines:
                    if line.startswith("lang = "):
                        f.write("lang = \"" + language + "\"\n")
                    else:
                        f.write(line)
        # Get unique labels
        labels = set([x[1] for x in self.__get_data_from_database__(host, database, table_name)])
        db = spacy.tokens.DocBin()
        train = []
        dev = []
        all = []
        for text, label in self.__get_data_from_database__(host, database, table_name):
            doc = nlp.make_doc(text)
            # set doc label
            for lbl in labels:
                if lbl == label:
                    doc.cats[lbl] = 1.0
                else:
                    doc.cats[lbl] = 0.0
            all.append(doc)
        # The dev.spacy file should look exactly the same as the train.spacy file, but should contain new examples that the training process hasn't seen before to get a realistic evaluation of the performance of your model.
        from spacy.cli.train import train
        # split the training data to 20% dev data
        if len(all) >= 5:
            train_data, test_data = all[:int(len(all) * 0.2)], all[int(len(all) * 0.2):]
        else:
            train_data, test_data = all, all
        # Create docbin
        train_db = spacy.tokens.DocBin(docs=train_data)
        dev_db = spacy.tokens.DocBin(docs=test_data)
        # Delete files if they exist
        if os.path.exists("./train.spacy"):
            os.remove("./train.spacy")
        if os.path.exists("./dev.spacy"):
            os.remove("./dev.spacy")
        train_db.to_disk("./train.spacy")
        dev_db.to_disk("./dev.spacy")
        train(config_path=cfg, output_path="./output")
        # move the model to the given path
        # delete the folder with the same name as the model_name if it exists
        if os.path.exists(folder + "/" + model_name):
            shutil.rmtree(folder + "/" + model_name)
        source_dir = "./output/model-best"
        shutil.copytree(source_dir, folder + "/" + model_name)


