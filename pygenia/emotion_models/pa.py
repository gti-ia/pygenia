import math
import os
import pandas as pd
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
            "pa_language_models/english_emotions.csv",
            "pa_language_models/english_intensity.csv",
        ],
    ):
        self.emotion_parameters = self.load_emotion_labels(
            os.path.join(this_path, parameters[0])
        )

        self.intensity_parameters = self.load_intensity_labels(
            os.path.join(this_path, parameters[1])
        )
        print(self.intensity_parameters)
        exit()

    def emotion_degree(self):
        angle: float = math.atan2(self.arousal, self.pleasure) * 180 / math.pi
        if angle < 0.0:
            angle += 360
        return angle

    def emotion_intensity(self):
        return (
            math.round(
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
