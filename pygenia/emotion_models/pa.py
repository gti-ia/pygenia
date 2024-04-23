import math
import os
import pandas as pd
import numpy as np
from scipy.special import iv
from pygenia.emotion_models.affective_state import AffectiveState

this_path = os.path.dirname(os.path.abspath(__file__))


class Point:
    def __init__(self, pleasure, arousal):
        self.pleasure = pleasure
        self.arousal = arousal

    def set_pleasure(self, pleasure):
        self.pleasure = pleasure

    def set_arousal(self, arousal):
        self.arousal = arousal

    def get_pleasure(self):
        return self.pleasure

    def get_arousal(self):
        return self.arousal

    def __str__(self):
        return f"({self.pleasure}, {self.arousal})"

    def __repr__(self):
        return f"Point({self.pleasure}, {self.arousal})"


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
                "spanish",
            ]

        if len(parameters) < 1:
            raise IndexError(
                "PA parameters must have 1 components give: '%d'" % len(parameters)
            )

        self.emotion_parameters = self.load_csv(
            os.path.join(
                this_path, "pa_language_models/emotion_label/" + parameters[0] + ".csv"
            )
        )

        self.intensity_parameters = self.load_csv(
            os.path.join(
                this_path,
                "pa_language_models/emotion_intensity/" + parameters[0] + ".csv",
            )
        )

        self.appraisal_parameters = self.load_csv(
            os.path.join(
                this_path,
                "pa_language_models/appraisal_variables/" + parameters[0] + ".csv",
            )
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
            emotion = emotion[0]

            self.mood.pleasure, self.mood.arousal = self.vector_sum(self.mood, emotion)
            self.affective_labels = self.fuzzify_emotion(self.mood)

    def deriveASFromAppraisalVariables(self, affective_info):
        """
        This method is used to derive the affective state from the appraisal variables.

        Returns:
            PA: Affective state.
        """
        emotion = Point(pleasure=0.0, arousal=0.0)
        if (
            affective_info.get_appraisal_variables()["expectedness"] != None
            and affective_info.get_appraisal_variables()["expectedness"] < 0
        ):

            pleasure, arousal = self.calculate_coordinates(
                magnitude=0.5, angle=self.appraisal_parameters["angle"].iloc[0]
            )
            emotion.set_pleasure(emotion.get_pleasure() + pleasure)
            emotion.set_arousal(emotion.get_arousal() + arousal)
        if (
            affective_info.get_appraisal_variables()["desirability"] != None
            and affective_info.get_appraisal_variables()["likelihood"] != None
        ):
            if affective_info.get_appraisal_variables()["desirability"] > 0.5:
                if affective_info.get_appraisal_variables()["likelihood"] < 1:
                    pleasure, arousal = self.calculate_coordinates(
                        magnitude=0.5, angle=self.appraisal_parameters["angle"].iloc[1]
                    )
                    emotion.set_pleasure(emotion.get_pleasure() + pleasure)
                    emotion.set_arousal(emotion.get_arousal() + arousal)
                elif affective_info.get_appraisal_variables()["likelihood"] == 1:
                    pleasure, arousal = self.calculate_coordinates(
                        magnitude=0.5, angle=self.appraisal_parameters["angle"].iloc[2]
                    )
                    emotion.set_pleasure(emotion.get_pleasure() + pleasure)
                    emotion.set_arousal(emotion.get_arousal() + arousal)
            else:
                if affective_info.get_appraisal_variables()["likelihood"] < 1:
                    pleasure, arousal = self.calculate_coordinates(
                        magnitude=0.5, angle=self.appraisal_parameters["angle"].iloc[3]
                    )
                    emotion.set_pleasure(emotion.get_pleasure() + pleasure)
                    emotion.set_arousal(emotion.get_arousal() + arousal)
                elif affective_info.get_appraisal_variables()["likelihood"] == 1:
                    pleasure, arousal = self.calculate_coordinates(
                        magnitude=0.5, angle=self.appraisal_parameters["angle"].iloc[4]
                    )
                    emotion.set_pleasure(emotion.get_pleasure() + pleasure)
                    emotion.set_arousal(emotion.get_arousal() + arousal)
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
                    pleasure, arousal = self.calculate_coordinates(
                        magnitude=0.5, angle=self.appraisal_parameters["angle"].iloc[5]
                    )
                    emotion.set_pleasure(emotion.get_pleasure() + pleasure)
                    emotion.set_arousal(emotion.get_arousal() + arousal)

        return [emotion]

    def vector_sum(
        self, vector1: Point, vector2: Point, weight1: float = 1.0, weight2: float = 1.0
    ):
        sum_x = max(0, min(1, vector1.pleasure * weight1 + vector2.pleasure * weight2))
        sum_y = max(0, min(1, vector1.arousal * weight1 + vector2.arousal * weight2))

        return sum_x, sum_y

    def is_affective_relevant(self, event):
        pass

    def clone(self):
        pass

    def get_affective_labels(self):
        return self.affective_labels

    def emotion_degree(self, vector: Point):

        return math.atan2(vector.arousal, vector.pleasure)

    def emotion_intensity(self, vector: Point):
        return (
            round(
                math.sqrt(
                    (vector.pleasure * vector.pleasure)
                    + (vector.arousal * vector.arousal)
                )
                * 1000.0
            )
            / 1000.0
        )

    def load_csv(self, path):
        return pd.read_csv(path, header=0)

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

    def fuzzify_intensity(self, vector: Point):
        intensity = self.emotion_intensity(vector)
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

    def fuzzify_emotion(self, vector: Point):
        degree = self.emotion_degree(vector)
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
