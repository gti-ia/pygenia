import math
import os
import pandas as pd
import numpy as np
from scipy.special import iv
from pygenia.emotion_models.affective_state import AffectiveState
from typing import Union
from collections import namedtuple

this_path = os.path.dirname(os.path.abspath(__file__))


class PAModel(AffectiveState):
    def __init__(self) -> None:
        super().__init__()
        self.mood = Point(pleasure=0.0, arousal=0.0)
        self.emotion_parameters = None
        self.intensity_parameters = None
        self.affective_labels = []

    def init_parameters(
        self,
        parameters=None,
    ):
        if parameters is None:
            parameters = [
                "pa_language_models/spanish_emotions.csv",
                "pa_language_models/spanish_intensity.csv",
            ]

        self.emotion_parameters = self.load_emotion_labels(
            os.path.join(this_path, parameters[0])
        )

        self.intensity_parameters = self.load_intensity_labels(
            os.path.join(this_path, parameters[1])
        )
        self.stimate_min_max()

    def estimate_emotion(self, affective_info):
        affective_info.set_elicited_emotions(
            self.deriveASFromAppraisalVariables(affective_info)
        )

    def update_affective_state(self, affective_info):
        """
        This method is used to update the affective state

        """
        emotion = affective_info.get_elicited_emotions()
        if len(emotion) > 0:
            emotion = (emotion[0].pleasure, emotion[0].arousal)

            self.pleasure, self.arousal = self.vector_sum(
                (self.pleasure, self.arousal), emotion
            )
            self.affective_labels = self.fuzzify_emotion()

    def deriveASFromAppraisalVariables(self, affective_info):
        """
        This method is used to derive the affective state from the appraisal variables.

        Returns:
            PA: Affective state.
        """
        point = namedtuple("point", ["pleasure", "arousal"])
        emotion = point(pleasure=0.0, arousal=0.0)

        if (
            affective_info.get_appraisal_variables()["expectedness"] != None
            and affective_info.get_appraisal_variables()["expectedness"] < 0
        ):
            emotion._replace(pleasure=emotion[0] + 0.4)
            emotion._replace(arousal=emotion[0] + 0.67)
        if (
            affective_info.get_appraisal_variables()["desirability"] != None
            and affective_info.get_appraisal_variables()["likelihood"] != None
        ):
            if affective_info.get_appraisal_variables()["desirability"] > 0.5:
                if affective_info.get_appraisal_variables()["likelihood"] < 1:
                    emotion._replace(pleasure=emotion[0] + 0.2)
                    emotion._replace(arousal=emotion[0] + 0.2)
                elif affective_info.get_appraisal_variables()["likelihood"] == 1:
                    emotion._replace(pleasure=emotion[0] + 0.78)
                    emotion._replace(arousal=emotion[0] + 0.48)
            else:
                if affective_info.get_appraisal_variables()["likelihood"] < 1:
                    emotion._replace(pleasure=emotion[0] - 0.64)
                    emotion._replace(arousal=emotion[0] + 0.60)
                elif affective_info.get_appraisal_variables()["likelihood"] == 1:
                    emotion._replace(pleasure=emotion[0] - 0.63)
                    emotion._replace(arousal=emotion[0] - 0.27)
                if (
                    affective_info.get_appraisal_variables()["causal_attribution"]
                    != None
                    and affective_info.get_appraisal_variables()["controllability"]
                    != None
                    and affective_info.get_appraisal_variables()["causal_attribution"]
                    == "other"
                    and affective_info.get_appraisal_variables()["controllability"]
                    > 0.7
                ):
                    emotion._replace(pleasure=emotion[0] - 0.51)
                    emotion._replace(arousal=emotion[0] + 0.59)

        return emotion

    def vector_sum(self, vector1, vector2, weight1=1, weight2=1):
        if len(vector1) != 2 or len(vector2) != 2:
            raise ValueError("Vectors must be bidimensional.")
        sum_x = max(0, min(1, vector1[0] * weight1 + vector2[0] * weight2))
        sum_y = max(0, min(1, vector1[1] * weight1 + vector2[1] * weight2))

        return sum_x, sum_y

    def is_affective_relevant(self, event):
        pass

    def clone(self):
        pass

    def get_affective_labels(self):
        return self.affective_labels

    def emotion_degree(self):
        return math.atan2(self.arousal, self.pleasure)

    def emotion_intensity(self):
        return (
            round(
                math.sqrt(
                    (self.pleasure * self.pleasure) + (self.arousal * self.arousal)
                )
                * 1000.0
            )
            / 1000.0
        )

    def load_emotion_labels(self, emotion_labels_file):
        return pd.read_csv(emotion_labels_file, header=0)

    def load_intensity_labels(self, intensity_labels_file):
        return pd.read_csv(intensity_labels_file, header=0)

    def stimate_min_max(self):
        x_values = np.linspace(0, 2 * np.pi, 100)
        max_values = []
        min_values = []
        for i in range(len(self.emotion_parameters["label"])):
            y_values = self.von_mises(
                x_values,
                self.emotion_parameters["mean"].iloc[i],
                1 / self.emotion_parameters["sd"].iloc[i],
            )
            max_values.append(np.max(y_values))
            min_values.append(np.min(y_values))
        self.emotion_parameters.loc[:, "max"] = max_values
        self.emotion_parameters.loc[:, "min"] = min_values

    def fuzzify_intensity(self):
        intensity = self.emotion_intensity()
        values = []
        for i in range(len(self.intensity_parameters["label"])):
            values.append(
                np.max(
                    [
                        np.min(
                            [
                                (
                                    (intensity - self.intensity_parameters["a"].iloc[i])
                                    / (
                                        self.intensity_parameters["b"].iloc[i]
                                        - self.intensity_parameters["a"].iloc[i]
                                    )
                                    if self.intensity_parameters["b"].iloc[i]
                                    - self.intensity_parameters["a"].iloc[i]
                                    > 0
                                    else math.inf
                                ),
                                1,
                                (
                                    (self.intensity_parameters["d"].iloc[i] - intensity)
                                    / (
                                        self.intensity_parameters["d"].iloc[i]
                                        - self.intensity_parameters["c"].iloc[i]
                                    )
                                    if self.intensity_parameters["d"].iloc[i]
                                    - self.intensity_parameters["c"].iloc[i]
                                    > 0
                                    else math.inf
                                ),
                            ]
                        ),
                        0,
                    ]
                )
            )
        df_result = self.intensity_parameters.copy()[["label"]]
        df_result.loc[:, "values"] = values
        return df_result[df_result["values"] == df_result["values"].max()][
            "label"
        ].tolist()

    def fuzzify_emotion(self):
        degree = self.emotion_degree()
        values = []
        for i in range(len(self.emotion_parameters["label"])):
            y_value = self.von_mises(
                degree,
                self.emotion_parameters["mean"].iloc[i],
                1 / self.emotion_parameters["sd"].iloc[i],
            )
            nomalized_y_value = (y_value - self.emotion_parameters["min"].iloc[i]) / (
                self.emotion_parameters["max"].iloc[i]
                - self.emotion_parameters["min"].iloc[i]
            )
            values.append(nomalized_y_value)

        df_result = self.emotion_parameters.copy()[["label"]]
        df_result.loc[:, "values"] = values
        return df_result[df_result["values"] == df_result["values"].max()][
            "label"
        ].tolist()

    def defuzzify_emotion(self, emotion: str, intensity: str):
        angle = (
            self.emotion_parameters.loc[self.emotion_parameters["label"] == emotion][
                ["mean"]
            ]
            .iloc[0]
            .iloc[0]
        )

        magnitude = (
            self.intensity_parameters.loc[
                self.intensity_parameters["label"] == intensity
            ][["b"]]
            .iloc[0]
            .iloc[0]
            + self.intensity_parameters.loc[
                self.intensity_parameters["label"] == intensity
            ][["c"]]
            .iloc[0]
            .iloc[0]
        ) / 2
        return self.calculate_coordinates(magnitude, angle)

    def calculate_coordinates(self, magnitude, angle):
        # Calculate x and y coordinates
        x_coordinate = magnitude * math.cos(angle)
        y_coordinate = magnitude * math.sin(angle)
        return x_coordinate, y_coordinate

    def von_mises(self, x, mu, kappa):
        return np.exp(kappa * np.cos(x - mu)) / (2 * np.pi * iv(0, kappa))


class Point:
    def __init__(self, pleasure, arousal):
        self.pleasure = pleasure
        self.arousal = arousal

    def __str__(self):
        return f"({self.pleasure}, {self.arousal})"

    def __repr__(self):
        return f"Point({self.pleasure}, {self.arousal})"
