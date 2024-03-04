class AffectiveState:
    """
    This class is used to represent the affective state of the agent
    """

    components = None
    affectiveLabels = None

    def __init__(self):
        self.affective_labels = []

    def update_affective_state(self):
        """
        This method is used to update the affective state

        """
        pass

    def init_parameters(self, parameters):
        pass

    def is_affective_relevant(self, event):
        pass

    def clone(self):
        pass

    def get_affective_labels(self):
        return self.affective_labels
