from pygenia.affective_state.pad import PAD


class TemporalAffectiveInformation:
    def __init__(self):
        self.temp_beliefs = {"Ba": [], "Br": [], "st": None}
        self.appraisal_variables = None
        self.coping_strategies = None
        self.appraised_emotions = None
        self.empathic_emotions = None
        self.elicited_emotions = None
        self.mood = None
        self.set_appraisal_variables()
        self.set_mood()

    def get_temp_beliefs(self):
        return self.Temp_beliefs

    def set_temp_beliefs(self, value):
        self.Temp_beliefs = value

    # Getter y Setter for appraisal_variables
    def get_appraisal_variables(self):
        return self.appraisal_variables

    def set_appraisal_variables(self, appraisal_variables=None):
        if appraisal_variables is None:
            self.appraisal_variables = {
                "desirability": None,
                "likelihood": None,
                "causal_attribution": None,
                "controllability": None,
                "expectedness": None,
            }
        else:
            self.appraisal_variables = appraisal_variables

    # Getter y Setter for coping_strategies
    def get_coping_strategies(self):
        return self.coping_strategies

    def set_coping_strategies(self, value):
        self.coping_strategies = value

    # Getter y Setter for appraised_emotions
    def get_appraised_emotions(self):
        return self.appraised_emotions

    def set_appraised_emotions(self, value):
        self.appraised_emotions = value

    # Getter y Setter for empathic_emotions
    def get_empathic_emotions(self):
        return self.empathic_emotions

    def set_empathic_emotions(self, value):
        self.empathic_emotions = value

    # Getter y Setter for elicited_emotions
    def get_elicited_emotions(self):
        return self.elicited_emotions

    def set_elicited_emotions(self, value):
        self.elicited_emotions = value

    # Getter y Setter for mood
    def get_mood(self):
        return self.mood

    def set_mood(self, mood=None):
        if mood is None:
            self.mood = PAD()
        else:
            self.mood = mood
