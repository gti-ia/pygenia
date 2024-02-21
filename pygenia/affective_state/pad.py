from enum import Enum
import numpy as np

from pygenia.affective_state.affective_state import AffectiveState


class PAD(AffectiveState):
    """
    This class is used to represent the PAD of the agent
    """

    class PADlabels(Enum):
        pleassure = 0
        arousal = 1
        dominance = 2

    def __init__(self, p=None, a=None, d=None):
        super().__init__()
        if (p is not None) and (a is not None) and (d is not None):
            self.setP(p)
            self.setA(a)
            self.setD(d)
        self.affRevEventThreshold = None
        self.initAffectiveThreshold()

    def initAffectiveThreshold(self):
        """
        This method is used to initialize the affective thresholds of the agent.
        """

        self.DISPLACEMENT = 0.5
        self.affRevEventThreshold = []
        self.affRevEventThreshold.append(PADExpression(0.8, "or", 0.8, "and", 0.0))

    def setAffectiveLabels(self):
        """
        This method is used to set the affective labels
        """
        self.affectiveLabels.append(self.PADlabels.pleassure.name)
        self.affectiveLabels.append(self.PADlabels.arousal.name)
        self.affectiveLabels.append(self.PADlabels.dominance.name)

    def clone(self):
        """
        This method is used to clone the PAD

        Returns:
            PAD: Cloned PAD
        """
        pad = PAD()
        pad.init()
        for i in range(self.getComponentsNumber()):
            pad.getComponents().append(self.getComponents()[i])
        return pad

    @staticmethod
    def sameOctant(as1, as2):
        """
        This method is used to check if two affective states are in the same octant

        Args:
            as1 (PAD): Affective state 1
            as2 (PAD): Affective state 2

        Returns:
            bool: True if the affective states are in the same octant, False otherwise
        """
        result = False
        if as1 is not None and as2 is not None:
            result = (
                np.sign(as1.getP()) == np.sign(as2.getP())
                and np.sign(as1.getA()) == np.sign(as2.getA())
                and np.sign(as1.getD()) == np.sign(as2.getD())
            )
        return result

    @staticmethod
    def betweenVECandCenter(as1, as2):
        """
        This method is used to check if two affective states are between the vector and the center

        Args:
            as1 (PAD): Affective state 1
            as2 (PAD): Affective state 2

        Returns:
            bool: True if the affective states are between the vector and the center, False otherwise
        """
        result = False
        if as1 is not None and as2 is not None:
            result = (
                (
                    (as1.getP() < 0 and as2.getP() > as1.getP())
                    or (as1.getP() > 0 and as2.getP() < as1.getP())
                )
                or (
                    (as1.getA() < 0 and as2.getA() > as1.getA())
                    or (as1.getA() > 0 and as2.getA() < as1.getA())
                )
                or (
                    (as1.getD() < 0 and as2.getD() > as1.getD())
                    or (as1.getD() > 0 and as2.getD() < as1.getD())
                )
            )

        return result

    def getP(self):
        return self.components[self.PADlabels.pleassure.value]

    def setP(self, p):
        self.components[self.PADlabels.pleassure.value] = p

    def getA(self):
        return self.components[self.PADlabels.arousal.value]

    def setA(self, a):
        self.components[self.PADlabels.arousal.value] = a

    def getD(self):
        return self.components[self.PADlabels.dominance.value]

    def setD(self, d):
        self.components[self.PADlabels.dominance.value] = d


class PADExpression:
    """
    This class is used to represent the PAD expressions.

    PAD = {Pleasure, Arousal, Dominance}
    """

    def __init__(self, pThres, op1, aThres, op2, dThres):
        """
        Constructor of the PADExpression class.

        Args:
            pThres (float): Pleasure threshold.
            op1 (str): Operator 1.
            aThres (float): Arousal threshold.
            op2 (str): Operator 2.
            dThres (float): Dominance threshold.
        """
        self.PThreshold = pThres
        self.operator1 = op1
        self.AThreshold = aThres
        self.operator2 = op2
        self.DThreshold = dThres

    def evaluate(self, p, a, d) -> bool:
        """
        This method is used to evaluate the PAD expression.

        Args:
            p (float): Pleasure value.
            a (float): Arousal value.
            d (float): Dominance value.
        Returns:
            bool: True if the PAD expression is evaluated, False otherwise.
        """

        result = True
        if self.operator1 == "and":
            result = (p <= self.PThreshold) and (p <= self.AThreshold)
        else:
            result = (p <= self.PThreshold) or (p <= self.AThreshold)
        if self.operator2 == "and":
            result = result and (p <= self.AThreshold)
        else:
            result = result or (p <= self.AThreshold)
        return result
