import math
from pygenia.affective_state.affective_state import AffectiveState


class PAModel(AffectiveState):
    def __init__(self, path: str = "english") -> None:
        super().__init__()
        self.pleasure = 0.0
        self.arousal = 0.0

    def emotion_degree(self):
        angle: float = math.atan2(self.a, self.p) * 180 / math.pi
        if angle < 0.0:
            angle += 360
        return angle

    def emotion_intensity(self):
        return (
            math.round(math.sqrt((self.p * self.p) + (self.a * self.a)) * 1000.0)
            / 1000.0
        )

    def emotion_label(self):
        if self.language == "spanish":
            pass
        if self.language == "english":
            pass

    def emotion_intensity_label(self):
        pass
