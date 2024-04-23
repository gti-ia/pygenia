class Personality:
    """
    This class is used to represent the personality of the agent.

    """

    def __init__(self):
        """
        Constructor of the Personality class.
        """
        self.rationalityLevel = 0.0
        self.copingStrategies = []
        self.personality_parameters = None
        self.traits = None

    def get_traits(self):
        return self.traits

    def get_personality_parameters(self):
        return self.personality_parameters

    def emotion_regulation(self, emotion):
        return emotion

    def set_personality(self, attributes_dict=None, parameters=None):
        """
        This method is used to initialize the personality of the agent.
        """
        if attributes_dict is not None:
            self.init_attributes(attributes_dict)

        self.init_parameters(parameters)

    def init_attributes(self, attributes):
        pass

    def init_parameters(self, parameters):
        self.personality_parameters = parameters

    def clone(self):
        """
        This method is used to clone the personality of the agent.
        """
        return self

    def get_rationality_level(self):
        """
        This method is used to get the rationality level of the agent.

        Returns:
            float: Rationality level of the agent.
        """
        return self.rationalityLevel

    def set_rationality_level(self, rationalityLevel) -> None:
        """
        This method is used to set the rationality level of the agent.

        Args:
            rationalityLevel (float): Rationality level of the agent.
        """
        self.rationalityLevel = rationalityLevel

    def get_coping_strategies(self):
        """
        This method is used to get the coping strategies of the agent.

        Returns:
            list: Coping strategies of the agent.
        """
        return self.copingStrategies

    def set_coping_strategies(self, copingStrategies) -> None:
        """
        This method is used to set the coping strategies of the agent.

        Args:
            copingStrategies (list): Coping strategies of the agent.
        """
        self.copingStrategies = copingStrategies

    def set_personality_class(self, personality_cls):
        # Aquí puedes agregar cualquier validación adicional si es necesario
        self._personality_cls = personality_cls
