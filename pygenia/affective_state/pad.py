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

    def update_affective_state(self):
        """
        This method is used to update the affective state.
        """
        self.DISPLACEMENT = 0.5
        if isinstance(self.Ta["mood"], PAD):
            pad = PAD()
            calculated_as = self.deriveASFromAppraisalVariables()

            if calculated_as != None:
                # PAD current_as = (PAD) getAS();
                current_as = self.Ta["mood"]

                tmpVal = None
                vDiff_P = None
                vDiff_A = None
                vDiff_D = None
                vectorToAdd_P = None
                vectorToAdd_A = None
                vectorToAdd_D = None
                lengthToAdd = None
                VEC = calculated_as

                # Calculating the module of VEC
                VECmodule = math.sqrt(
                    math.pow(VEC.getP(), 2)
                    + math.pow(VEC.getA(), 2)
                    + math.pow(VEC.getD(), 2)
                )

                # 1 Applying the pull and push of ALMA
                if PAD.betweenVECandCenter(current_as, VEC) or not PAD.sameOctant(
                    current_as, VEC
                ):
                    vDiff_P = VEC.getP() - current_as.getP()
                    vDiff_A = VEC.getA() - current_as.getA()
                    vDiff_D = VEC.getD() - current_as.getD()
                else:
                    vDiff_P = current_as.getP() - VEC.getP()
                    vDiff_A = current_as.getA() - VEC.getA()
                    vDiff_D = current_as.getD() - VEC.getD()

                # 2 The module of the vector VEC () is multiplied by the DISPLACEMENT and this
                # is the length that will have the vector to be added to 'as'
                lengthToAdd = VECmodule * self.DISPLACEMENT

                # 3 Determining the vector to add
                vectorToAdd_P = vDiff_P * self.DISPLACEMENT
                vectorToAdd_A = vDiff_A * self.DISPLACEMENT
                vectorToAdd_D = vDiff_D * self.DISPLACEMENT

                # 4 The vector vectorToAdd is added to 'as' and this is the new value of
                # the current affective state
                tmpVal = current_as.getP() + vectorToAdd_P
                if tmpVal > 1:
                    tmpVal = 1.0
                else:
                    if tmpVal < -1:
                        tmpVal = -1.0
                pad.setP(round(tmpVal * 10.0) / 10.0)
                tmpVal = current_as.getA() + vectorToAdd_A
                if tmpVal > 1:
                    tmpVal = 1.0
                else:
                    if tmpVal < -1:
                        tmpVal = -1.0
                pad.setA(round(tmpVal * 10.0) / 10.0)
                tmpVal = current_as.getD() + vectorToAdd_D
                if tmpVal > 1:
                    tmpVal = 1.0
                else:
                    if tmpVal < -1:
                        tmpVal = -1.0
                pad.setD(round(tmpVal * 10.0) / 10.0)

                self.Ta["mood"] = pad
                AClabel = self.getACLabel()
                self.AfE = AClabel
        pass

    def getACLabel(self):
        """
        This method is used to get the affective category label.

        Returns:
            list: Affective category label.
        """

        result = []
        matches = True
        r = None
        for acl in self.affective_categories.keys():
            matches = True
            if self.affective_categories[acl] != None:
                if len(self.affective_categories[acl]) == len(
                    self.affective_info.get_mood().affectiveLabels
                ):
                    for i in range(len(self.affective_info.get_mood().affectiveLabels)):
                        r = self.affective_categories[acl][i]
                        matches = (
                            matches
                            and self.affective_info.get_mood().components[i] >= r[0]
                            and self.affective_info.get_mood().components[i] <= r[1]
                        )
                else:
                    try:
                        raise Exception(
                            "The number of components for the affective category "
                            + acl
                            + " must be the same as the number of the components for the affective state"
                        )
                    except Exception as e:
                        print(e)
            if matches:
                result.append(acl)
        return result

    def deriveASFromAppraisalVariables(self):
        """
        This method is used to derive the affective state from the appraisal variables.

        Returns:
            PAD: Affective state.
        """
        em = []

        if (
            self.affective_info.get_appraisal_variables()["expectedness"] != None
            and self.affective_info.get_appraisal_variables()["expectedness"] < 0
        ):
            em.append("surprise")
        if (
            self.affective_info.get_appraisal_variables()["desirability"] != None
            and self.affective_info.get_appraisal_variables()["likelihood"] != None
        ):
            if self.affective_info.get_appraisal_variables()["desirability"] > 0.5:
                if self.affective_info.get_appraisal_variables()["likelihood"] < 1:
                    em.append("hope")
                elif self.affective_info.get_appraisal_variables()["likelihood"] == 1:
                    em.append("joy")
            else:
                if self.affective_info.get_appraisal_variables()["likelihood"] < 1:
                    em.append("fear")
                elif self.affective_info.get_appraisal_variables()["likelihood"] == 1:
                    em.append("sadness")
                if (
                    self.affective_info.get_appraisal_variables()["causal_attribution"]
                    != None
                    and self.affective_info.get_appraisal_variables()["controllability"]
                    != None
                    and self.affective_info.get_appraisal_variables()[
                        "causal_attribution"
                    ]
                    == "other"
                    and self.affective_info.get_appraisal_variables()["controllability"]
                    > 0.7
                ):
                    em.append("anger")
        result = PAD()
        result.setP(0.0)
        result.setA(0.0)
        result.setD(0.0)

        for e in em:
            if e == "anger":
                result.setP(result.getP() - 0.51)
                result.setA(result.getA() + 0.59)
                result.setD(result.getD() + 0.25)
            elif e == "fear":
                result.setP(result.getP() - 0.64)
                result.setA(result.getA() + 0.60)
                result.setD(result.getD() - 0.43)
            elif e == "hope":
                result.setP(result.getP() + 0.2)
                result.setA(result.getA() + 0.2)
                result.setD(result.getD() - 0.1)
            elif e == "joy":
                result.setP(result.getP() + 0.76)
                result.setA(result.getA() + 0.48)
                result.setD(result.getD() + 0.35)
            elif e == "sadness":
                result.setP(result.getP() - 0.63)
                result.setA(result.getA() - 0.27)
                result.setD(result.getD() - 0.33)
            elif e == "surprise":
                result.setP(result.getP() + 0.4)
                result.setA(result.getA() + 0.67)
                result.setD(result.getD() - 0.13)

        # Averaging
        if len(em) > 0:
            result.setP(result.getP() / len(em))
            result.setA(result.getA() / len(em))
            result.setD(result.getD() / len(em))
        else:
            result = None
        return result


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
