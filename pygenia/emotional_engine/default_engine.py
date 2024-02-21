import collections
from pygenia.emotional_engine.as_utils import TemporalAffectiveInformation
from pygenia.emotional_engine.emotional_engine import EmotionalEngine


class DefaultEngine(EmotionalEngine):
    def __init__(self):
        super(EmotionalEngine, self).__init__()
        self.circunstance = {"I": collections.deque(), "E": [], "A": []}
        self.temporal_information = TemporalAffectiveInformation()
        self.affective_categories = {
            "neutral": [
                [-0.3, 0.3],
                [-0.3, 0.3],
                [-1, 1],
            ],
            "happy": [[0, 1], [0, 1], [-1, 1]],
            "sad": [[-1, 0], [-1, 0], [-1, 1]],
        }

    def UpdateAS(self):
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
