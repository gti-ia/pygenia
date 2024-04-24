class Personality:
    """
    This class is used to represent the personality of the agent.

    """

    def __init__(self):
        """
        Constructor of the Personality class.
        """
        self.rationality_level = 0.0
        # Empathic level
        self.empathic_level = 0.0
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
        return self.rationality_level

    def set_rationality_level(self, rationality_level) -> None:
        """
        This method is used to set the rationality level of the agent.

        Args:
            rationality_level (float): Rationality level of the agent.
        """
        self.rationality_level = rationality_level

    def get_empathic_level(self):
        """
        This method is used to get the empathic level of the agent.

        Returns:
            float: Empathic level of the agent.
        """
        return self.empathic_level

    def set_empathic_level(self, empathic_level) -> None:
        """
        This method is used to set the empathic level of the agent.

        Args:
            empathic_level (float): Empathic level of the agent.
        """
        self.empathic_level = empathic_level

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
