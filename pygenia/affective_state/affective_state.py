class AffectiveState:
    """
    This class is used to represent the affective state of the agent
    """

    components = None
    affectiveLabels = None

    def __init__(self):
        self.init()

    def init(self):
        self.affectiveLabels = []
        self.components = []
        self.setAffectiveLabels()
        if self.affectiveLabels:
            for i in range(len(self.affectiveLabels)):
                self.components.append(0.0)
        self.components = [0.0 for i in range(len(self.affectiveLabels))]

    def setAffectiveLabels(self):
        """
        This method is used to set the affective labels

        """
        pass

    def getAffectiveLabels(self):
        """
        This method is used to get the affective labels

        Returns:
            list: Affective labels
        """
        return self.affectiveLabels

    def getComponents(self):
        """
        This method is used to get the components of the affective state

        Returns:
            list: Components of the affective state
        """
        return self.components

    def setComponents(self, comp):
        """
        This method is used to set the components of the affective state

        Args:
            comp (list): Components of the affective state
        """
        if comp:
            if self.propperSize(len(comp)):
                self.components = comp
            else:
                raise Exception("Incorrect input data size")

    def getComponentsNumber(self):
        """
        This method is used to get the number of components of the affective state

        Returns:
            int: Number of components of the affective state
        """
        nr = 0
        if self.components:
            nr = len(self.components)
        return nr

    def propperSize(self, size):
        """
        This method is used to check if the size of the affective state is correct

        Args:
            size (int): Size of the affective state

        Returns:
            bool: True if the size of the affective state is correct, False otherwise
        """
        result = False
        if self.components:
            result = size == len(self.components)
        else:
            result = True
        return result

    def clone(self):
        pass
