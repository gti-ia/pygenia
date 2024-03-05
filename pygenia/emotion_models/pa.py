import math
import os
import pandas as pd
import numpy as np
from scipy.special import iv
from pygenia.emotion_models.affective_state import AffectiveState

this_path = os.path.dirname(os.path.abspath(__file__))


class PAModel(AffectiveState):
    def __init__(self) -> None:
        super().__init__()
        self.pleasure = 0.0
        self.arousal = 0.0
        self.emotion_parameters = None
        self.intensity_parameters = None

    def init_parameters(
        self,
        parameters=[
            "pa_language_models/spanish_emotions.csv",
            "pa_language_models/spanish_intensity.csv",
        ],
    ):
        self.emotion_parameters = self.load_emotion_labels(
            os.path.join(this_path, parameters[0])
        )

        self.intensity_parameters = self.load_intensity_labels(
            os.path.join(this_path, parameters[1])
        )

        self.stimate_min_max()
        self.fuzzify_emotion()

    def emotion_degree(self):
        angle: float = math.atan2(self.arousal, self.pleasure) * 180 / math.pi
        if angle < 0.0:
            angle += 360
        return angle

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

    def emotion_intensity_label(self):
        pass

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
        degree = 0.0

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

    def von_mises(self, x, mu, kappa):
        return np.exp(kappa * np.cos(x - mu)) / (2 * np.pi * iv(0, kappa))
