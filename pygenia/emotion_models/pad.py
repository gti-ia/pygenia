from enum import Enum
import math
import numpy as np

from pygenia.emotion_models.affective_state import AffectiveState


class PAD(AffectiveState):
    """
    This class is used to represent the PAD of the agent
    """

    class PADlabels(Enum):
        pleasure = 0
        arousal = 1
        dominance = 2

    def __init__(self):
        super().__init__()
        self.p = 0.0
        self.a = 0.0
        self.d = 0.0
        self.displacement = 0.5
        self.affRevEventThreshold = []
        self.affective_dimensions = {}
        self.affective_labels = []
        self.initAffectiveThreshold()
        self.set_affective_dimensions()
        self.affective_categories = None

    def init_parameters(self, parameters=None):
        if parameters is not None:
            self.affective_categories = parameters
        else:
            self.affective_categories = {
                "neutral": [
                    [-0.3, 0.3],
                    [-0.3, 0.3],
                    [-1, 1],
                ],
                "happy": [[0, 1], [0, 1], [-1, 1]],
                "sad": [[-1, 0], [-1, 0], [-1, 1]],
            }

    def is_affective_relevant(self, event):
        event.evaluate(
            self.get_pleasure(),
            self.get_arousal(),
            self.get_dominance(),
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
                np.sign(as1.get_pleasure()) == np.sign(as2.get_pleasure())
                and np.sign(as1.get_arousal()) == np.sign(as2.get_arousal())
                and np.sign(as1.get_dominance()) == np.sign(as2.get_dominance())
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
                    (as1.get_pleasure() < 0 and as2.get_pleasure() > as1.get_pleasure())
                    or (
                        as1.get_pleasure() > 0
                        and as2.get_pleasure() < as1.get_pleasure()
                    )
                )
                or (
                    (as1.get_arousal() < 0 and as2.get_arousal() > as1.get_arousal())
                    or (as1.get_arousal() > 0 and as2.get_arousal() < as1.get_arousal())
                )
                or (
                    (
                        as1.get_dominance() < 0
                        and as2.get_dominance() > as1.get_dominance()
                    )
                    or (
                        as1.get_dominance() > 0
                        and as2.get_dominance() < as1.get_dominance()
                    )
                )
            )

        return result

    def get_pleasure(self):
        return self.affective_dimensions[self.PADlabels.pleasure]

    def setP(self, p):
        self.affective_dimensions[self.PADlabels.pleasure] = p

    def get_arousal(self):
        return self.affective_dimensions[self.PADlabels.arousal]

    def setA(self, a):
        self.affective_dimensions[self.PADlabels.arousal] = a

    def get_dominance(self):
        return self.affective_dimensions[self.PADlabels.dominance]

    def setD(self, d):
        self.affective_dimensions[self.PADlabels.dominance] = d

    def estimate_emotion(self, affective_info):
        affective_info.set_elicited_emotions(
            self.deriveASFromAppraisalVariables(affective_info)
        )

    def update_affective_state(self, emotions):
        """
        This method is used to update the affective state.
        """
        self.displacement = 0.5
        calculated_as = (
            emotions
        )  # self.deriveASFromAppraisalVariables(affective_info)

        if calculated_as is not None:
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
                math.pow(VEC.get_pleasure(), 2)
                + math.pow(VEC.get_arousal(), 2)
                + math.pow(VEC.get_dominance(), 2)
            )

            # 1 Applying the pull and push of ALMA
            if PAD.betweenVECandCenter(self, VEC) or not PAD.sameOctant(self, VEC):
                vDiff_P = VEC.get_pleasure() - self.get_pleasure()
                vDiff_A = VEC.get_arousal() - self.get_arousal()
                vDiff_D = VEC.get_dominance() - self.get_dominance()
            else:
                vDiff_P = self.get_pleasure() - VEC.get_pleasure()
                vDiff_A = self.get_arousal() - VEC.get_arousal()
                vDiff_D = self.get_dominance() - VEC.get_dominance()

            # 2 The module of the vector VEC () is multiplied by the DISPLACEMENT and this
            # is the length that will have the vector to be added to 'as'
            lengthToAdd = VECmodule * self.displacement

            # 3 Determining the vector to add
            vectorToAdd_P = vDiff_P * self.displacement
            vectorToAdd_A = vDiff_A * self.displacement
            vectorToAdd_D = vDiff_D * self.displacement

            # 4 The vector vectorToAdd is added to 'as' and this is the new value of
            # the current affective state
            tmpVal = self.get_pleasure() + vectorToAdd_P
            if tmpVal > 1:
                tmpVal = 1.0
            else:
                if tmpVal < -1:
                    tmpVal = -1.0
            self.setP(round(tmpVal * 10.0) / 10.0)
            tmpVal = self.get_arousal() + vectorToAdd_A
            if tmpVal > 1:
                tmpVal = 1.0
            else:
                if tmpVal < -1:
                    tmpVal = -1.0
            self.setA(round(tmpVal * 10.0) / 10.0)
            tmpVal = self.get_dominance() + vectorToAdd_D
            if tmpVal > 1:
                tmpVal = 1.0
            else:
                if tmpVal < -1:
                    tmpVal = -1.0
            self.setD(round(tmpVal * 10.0) / 10.0)

            # ffective_info.set_mood(pad)
            AClabel = self.getACLabel()
            self.affective_labels = AClabel
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
                    self.affective_dimensions
                ):

                    matches = (
                        matches
                        and self.affective_dimensions[self.PADlabels.pleasure]
                        >= self.affective_categories[acl][
                            self.PADlabels.pleasure.value
                        ][0]
                        and self.affective_dimensions[self.PADlabels.pleasure]
                        <= self.affective_categories[acl][
                            self.PADlabels.pleasure.value
                        ][1]
                        and self.affective_dimensions[self.PADlabels.arousal]
                        >= self.affective_categories[acl][self.PADlabels.arousal.value][
                            0
                        ]
                        and self.affective_dimensions[self.PADlabels.arousal]
                        <= self.affective_categories[acl][self.PADlabels.arousal.value][
                            1
                        ]
                        and self.affective_dimensions[self.PADlabels.dominance]
                        >= self.affective_categories[acl][
                            self.PADlabels.dominance.value
                        ][0]
                        and self.affective_dimensions[self.PADlabels.dominance]
                        <= self.affective_categories[acl][
                            self.PADlabels.dominance.value
                        ][1]
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
                result.setP(result.get_pleasure() - 0.51)
                result.setA(result.get_arousal() + 0.59)
                result.setD(result.get_dominance() + 0.25)
            elif e == "fear":
                result.setP(result.get_pleasure() - 0.64)
                result.setA(result.get_arousal() + 0.60)
                result.setD(result.get_dominance() - 0.43)
            elif e == "hope":
                result.setP(result.get_pleasure() + 0.2)
                result.setA(result.get_arousal() + 0.2)
                result.setD(result.get_dominance() - 0.1)
            elif e == "joy":
                result.setP(result.get_pleasure() + 0.76)
                result.setA(result.get_arousal() + 0.48)
                result.setD(result.get_dominance() + 0.35)
            elif e == "sadness":
                result.setP(result.get_pleasure() - 0.63)
                result.setA(result.get_arousal() - 0.27)
                result.setD(result.get_dominance() - 0.33)
            elif e == "surprise":
                result.setP(result.get_pleasure() + 0.4)
                result.setA(result.get_arousal() + 0.67)
                result.setD(result.get_dominance() - 0.13)

        # Averaging
        if len(em) > 0:
            result.setP(result.get_pleasure() / len(em))
            result.setA(result.get_arousal() / len(em))
            result.setD(result.get_dominance() / len(em))
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
