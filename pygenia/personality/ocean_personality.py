import math
import os
import pandas as pd

from pygenia.emotion_models.pa import Point
from pygenia.personality.personality import Personality

this_path = os.path.dirname(os.path.abspath(__file__))


class OceanPersonality(Personality):
    def __init__(self):
        self.personality_parameters = None

    def init_attributes(self, attributes_dict):
        required_keys = {"O", "C", "E", "A", "N"}
        if not required_keys.issubset(attributes_dict.keys()):
            raise ValueError("Dictionary must contain all required keys: O, C, E, A, N")
        self.traits = attributes_dict

    def init_parameters(
        self,
        parameters=None,
    ):
        if parameters is None:
            parameters = [
                "spanish",
            ]

        if len(parameters) < 1:
            raise IndexError(
                "PA parameters must have 1 components give: '%d'" % len(parameters)
            )

        self.personality_parameters = pd.read_csv(
            os.path.join(this_path, "ocean_language_models/" + parameters[0] + ".csv"),
            header=0,
        )
        self.stimate_personality_parameters_pa()

    def stimate_personality_parameters_pa(self):
        pleasure = []
        arousal = []
        for i in range(len(self.personality_parameters["label"])):
            pleasure.append(math.cos(self.personality_parameters["angle"].iloc[i]))
            arousal.append(math.sin(self.personality_parameters["angle"].iloc[i]))
        self.personality_parameters.loc[:, "p"] = pleasure
        self.personality_parameters.loc[:, "a"] = arousal

    def emotion_regulation(self, emotion: Point, weight=0.1):
        for i in range(len(self.personality_parameters["label"])):
            pleasure = (
                weight
                * self.traits[self.personality_parameters["label"].iloc[i]]
                * self.personality_parameters["p"].iloc[i]
                + emotion.get_pleasure()
            )

            arousal = (
                weight
                * self.traits[self.personality_parameters["label"].iloc[i]]
                * self.personality_parameters["a"].iloc[i]
                + emotion.get_arousal()
            )

        return Point(pleasure, arousal)

    def get_O(self):
        return self.traits["O"]

    def set_O(self, value):
        self.traits["O"] = value

    def get_C(self):
        return self.traits["C"]

    def set_C(self, value):
        self.traits["C"] = value

    def get_E(self):
        return self.traits["E"]

    def set_E(self, value):
        self.traits["E"] = value

    def get_A(self):
        return self.traits["A"]

    def set_A(self, value):
        self.traits["A"] = value

    def get_N(self):
        return self.traits["N"]

    def set_N(self, value):
        self.traits["N"] = value
