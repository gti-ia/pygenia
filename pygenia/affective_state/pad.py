from enum import Enum
import math
import numpy as np

from pygenia.affective_state.affective_state import AffectiveState


class PAD(AffectiveState):
    """
    This class is used to represent the PAD of the agent
    """

    class PADlabels(Enum):
        pleasure = 0
        arousal = 1
        dominance = 2

    def __init__(self, p=0.0, a=0.0, d=0.0):
        super().__init__()
        self.p = p
        self.a = a
        self.d = d
        self.displacement = 0.5
        self.affRevEventThreshold = []
        self.affective_dimensions = {}
        self.affective_labels = []
        self.initAffectiveThreshold()
        self.set_affective_dimensions()

    def is_affective_relevant(self, event):
        event.evaluate(
            self.getP(),
            self.getA(),
            self.getD(),
        )

    def initAffectiveThreshold(self):
        """
        This method is used to initialize the affective thresholds of the agent.
        """
        self.affRevEventThreshold.append(PADExpression(0.8, "or", 0.8, "and", 0.0))

    def set_affective_dimensions(self):
        """
        This method is used to set the affective labels
        """
        self.affective_dimensions.setdefault(self.PADlabels.pleasure, 0.0)
        self.affective_dimensions.setdefault(self.PADlabels.arousal, 0.0)
        self.affective_dimensions.setdefault(self.PADlabels.dominance, 0.0)

    def clone(self):
        """
        This method is used to clone the PAD

        Returns:
            PAD: Cloned PAD
        """
        pad = self
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
        return self.affective_dimensions[self.PADlabels.pleasure]

    def setP(self, p):
        self.affective_dimensions[self.PADlabels.pleasure] = p

    def getA(self):
        return self.affective_dimensions[self.PADlabels.arousal]

    def setA(self, a):
        self.affective_dimensions[self.PADlabels.arousal] = a

    def getD(self):
        return self.affective_dimensions[self.PADlabels.dominance]

    def setD(self, d):
        self.affective_dimensions[self.PADlabels.dominance] = d

    def update_affective_state(self, agent, affective_info, affective_categories):
        """
        This method is used to update the affective state.
        """
        self.displacement = 0.5
        pad = PAD()
        calculated_as = self.deriveASFromAppraisalVariables(affective_info)

        if calculated_as != None:
            # PAD current_as = (PAD) getAS();

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
            if PAD.betweenVECandCenter(self, VEC) or not PAD.sameOctant(self, VEC):
                vDiff_P = VEC.getP() - self.getP()
                vDiff_A = VEC.getA() - self.getA()
                vDiff_D = VEC.getD() - self.getD()
            else:
                vDiff_P = self.getP() - VEC.getP()
                vDiff_A = self.getA() - VEC.getA()
                vDiff_D = self.getD() - VEC.getD()

            # 2 The module of the vector VEC () is multiplied by the DISPLACEMENT and this
            # is the length that will have the vector to be added to 'as'
            lengthToAdd = VECmodule * self.displacement

            # 3 Determining the vector to add
            vectorToAdd_P = vDiff_P * self.displacement
            vectorToAdd_A = vDiff_A * self.displacement
            vectorToAdd_D = vDiff_D * self.displacement

            # 4 The vector vectorToAdd is added to 'as' and this is the new value of
            # the current affective state
            tmpVal = self.getP() + vectorToAdd_P
            if tmpVal > 1:
                tmpVal = 1.0
            else:
                if tmpVal < -1:
                    tmpVal = -1.0
            pad.setP(round(tmpVal * 10.0) / 10.0)
            tmpVal = self.getA() + vectorToAdd_A
            if tmpVal > 1:
                tmpVal = 1.0
            else:
                if tmpVal < -1:
                    tmpVal = -1.0
            pad.setA(round(tmpVal * 10.0) / 10.0)
            tmpVal = self.getD() + vectorToAdd_D
            if tmpVal > 1:
                tmpVal = 1.0
            else:
                if tmpVal < -1:
                    tmpVal = -1.0
            pad.setD(round(tmpVal * 10.0) / 10.0)

            affective_info.set_mood(pad)
            AClabel = self.getACLabel(affective_categories)
            self.affective_labels = AClabel
        pass

    def getACLabel(self, affective_categories):
        """
        This method is used to get the affective category label.

        Returns:
            list: Affective category label.
        """

        result = []
        matches = True
        r = None
        for acl in affective_categories.keys():
            matches = True
            if affective_categories[acl] != None:
                if len(affective_categories[acl]) == len(self.affective_dimensions):

                    matches = (
                        matches
                        and self.affective_dimensions[self.PADlabels.pleasure]
                        >= affective_categories[acl][self.PADlabels.pleasure.value][0]
                        and self.affective_dimensions[self.PADlabels.pleasure]
                        <= affective_categories[acl][self.PADlabels.pleasure.value][1]
                        and self.affective_dimensions[self.PADlabels.arousal]
                        >= affective_categories[acl][self.PADlabels.arousal.value][0]
                        and self.affective_dimensions[self.PADlabels.arousal]
                        <= affective_categories[acl][self.PADlabels.arousal.value][1]
                        and self.affective_dimensions[self.PADlabels.dominance]
                        >= affective_categories[acl][self.PADlabels.dominance.value][0]
                        and self.affective_dimensions[self.PADlabels.dominance]
                        <= affective_categories[acl][self.PADlabels.dominance.value][1]
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

    def deriveASFromAppraisalVariables(self, affective_info):
        """
        This method is used to derive the affective state from the appraisal variables.

        Returns:
            PAD: Affective state.
        """
        em = []

        if (
            affective_info.get_appraisal_variables()["expectedness"] != None
            and affective_info.get_appraisal_variables()["expectedness"] < 0
        ):
            em.append("surprise")
        if (
            affective_info.get_appraisal_variables()["desirability"] != None
            and affective_info.get_appraisal_variables()["likelihood"] != None
        ):
            if affective_info.get_appraisal_variables()["desirability"] > 0.5:
                if affective_info.get_appraisal_variables()["likelihood"] < 1:
                    em.append("hope")
                elif affective_info.get_appraisal_variables()["likelihood"] == 1:
                    em.append("joy")
            else:
                if affective_info.get_appraisal_variables()["likelihood"] < 1:
                    em.append("fear")
                elif affective_info.get_appraisal_variables()["likelihood"] == 1:
                    em.append("sadness")
                if (
                    affective_info.get_appraisal_variables()["causal_attribution"]
                    != None
                    and affective_info.get_appraisal_variables()["controllability"]
                    != None
                    and affective_info.get_appraisal_variables()["causal_attribution"]
                    == "other"
                    and affective_info.get_appraisal_variables()["controllability"]
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
