from pygenia.emotion_models.pad import PAD
from pygenia.emotion_models.pa import PAModel


class TemporalRationalInformation:
    def __init__(self):
        self._applicable_plan = None
        self._applicable_plans = []
        self._intention = None
        self._relevant_plans = []
        self._event = None

    def insert_applicable_plan(self, item):
        self._applicable_plan = item

    def insert_applicable_plans(self, item):
        self._applicable_plans.append(item)

    def delete_applicable_plans(self, item):
        if item in self._applicable_plans:
            self._applicable_plans.remove(item)
        else:
            print("Item not found in applicable_plans")

    def search_applicable_plans(self, item):
        return item in self._applicable_plans

    def insert_intention(self, item):
        self._intention = item

    def insert_relevant_plans(self, item):
        self._relevant_plans.append(item)

    def delete_relevant_plans(self, item):
        if item in self._relevant_plans:
            self._relevant_plans.remove(item)
        else:
            print("Item not found in relevant_plans")

    def search_relevant_plans(self, item):
        return item in self._relevant_plans

    def insert_event(self, item):
        self._event = item

    # Getter and setter for applicable_plan
    def get_applicable_plan(self):
        return self._applicable_plan

    def set_applicable_plan(self, value):
        self._applicable_plan = value

    # Getter and setter for applicable_plans
    def get_applicable_plans(self):
        return self._applicable_plans

    def set_applicable_plans(self, values):
        self._applicable_plans = values

    # Getter and setter for intention
    def get_intention(self):
        return self._intention

    def set_intention(self, value):
        self._intention = value

    # Getter and setter for relevant_plans
    def get_relevant_plans(self):
        return self._relevant_plans

    def set_relevant_plans(self, values):
        self._relevant_plans = values

    # Getter and setter for event
    def get_event(self):
        return self._event

    def set_event(self, value):
        self._event = value


class TemporalAffectiveInformation:
    def __init__(self, affst_cls=PAD):
        self.temp_beliefs = {"Ba": [], "Br": [], "st": None}
        self.appraisal_variables = None
        self.coping_strategies = []
        self.appraised_emotions = []
        self.empathic_emotions = []
        self.elicited_emotions = []
        self.mood = affst_cls()
        self.set_appraisal_variables()

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

    def set_mood(self, mood):
        self.mood = mood
