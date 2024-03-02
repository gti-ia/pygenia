from __future__ import print_function

import agentspeak
from pygenia.cognitive_engine.emotional_engine import EmotionalEngine
import random
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util
from pygenia.affective_state.affective_state import AffectiveState


LOGGER = agentspeak.get_logger(__name__)
C = {}


class DefaultEngine(EmotionalEngine):
    def __init__(self, agent):
        super().__init__(agent=agent)
        self.affective_categories = {
            "neutral": [
                [-0.3, 0.3],
                [-0.3, 0.3],
                [-1, 1],
            ],
            "happy": [[0, 1], [0, 1], [-1, 1]],
            "sad": [[-1, 0], [-1, 0], [-1, 1]],
        }

    def affective_transition_system(self):
        """
        This method is used to apply the second part of the reasoning cycle.
        This part consists of the following steps:
        - Appraisal
        - Update Aff State
        - Select Coping Strategy
        - Coping
        """

        options = {
            "Appr": self.applyAppraisal,
            "UpAs": self.applyUpdateAffState,
            "SelCs": self.applySelectCopingStrategy,
            "Cope": self.applyCope,
        }

        flag = True
        while flag == True and self.current_step_ast in options:
            flag = options[self.current_step_ast]()

        return True

    def applyAppraisal(self) -> bool:
        """
        This method is used to apply the appraisal process.
        """
        ped = PairEventDesirability(None)
        if True:  # while self.lock instead of True for the real implementation
            if self.event_queue:
                ped.event = self.event_queue.pop()

        if ped.event == None:
            self.appraisal(None, 0.0, self.concerns)
            self.currentEvent = None
            self.eventProcessedInCycle = False
        else:
            # TODO this cannot be a random value it must be calculated by the test_concern function
            self.appraisal(ped.event, random.random(), self.concerns)
            self.currentEvent = ped.event
            self.eventProcessedInCycle = True

        if self.cleanAffectivelyRelevantEvents():
            self.Mem = []

        # The next step is Update Aff State
        self.current_step_ast = "UpAs"
        return True

    def applyUpdateAffState(self):
        """
        This method is used to update the affective state.
        """
        if self.eventProcessedInCycle:
            self.update_affective_state()
        if self.isAffectRelevantEvent(self.currentEvent):
            self.Mem.append(self.currentEvent)
        self.current_step_ast = "SelCs"
        return True

    def selectCs(self):
        """
        This method is used to select the coping strategy.
        """
        """
        AClabel = self.C["AfE"]
        logCons = False
        asContainsCs = False
        if len(AClabel) != 0 and self.Ag["P"].getCopingStrategies() != None:
            for cs in self.Ag["P"].getCopingStrategies():
                if cs.getAffectCategory().name in AClabel:
                    logCons = cs.getContext().logicalConsequence(self.ag).hasNext()
                    if logCons:
                        self.C["CS"].append(cs)
                    asContainsCs = True
            if asContainsCs:
                self.C["AfE"] = []
        """
        pass

    def applyCope(self):
        """
        This method is used to apply the coping process.
        """

        SelectingCs = True
        while SelectingCs and self.affective_info.coping_strategies:
            SelectingCs = self.cope()
        # self.current_step_ast = "Appr"
        return False

    def cleanAffectivelyRelevantEvents(self) -> bool:
        return True

    def cope(self):
        """
        This method is used to apply the coping process.

        Returns:
            bool: True if the coping strategy was applied, False otherwise.
        """

        if self.affective_info.coping_strategies:
            cs = self.affective_info.coping_strategies.pop(0)
            self.affective_info.coping_strategies.append(cs)
            return True
        else:
            return False

    def applySelectCopingStrategy(self):
        """
        This method is used to select the coping strategy.
        Personality parser is not implemented yet.

        Returns:
            bool: True if the coping strategy was selected, False otherwise.
        """
        self.affective_info.coping_strategies = []
        # self.selectCs()
        self.current_step_ast = "Cope"
        return True

    def isAffectRelevantEvent(self, currentEvent):
        """
        This method is used to check if the event is affect relevant.

        Args:
            currentEvent (tuple): Event to be checked.

        Returns:
            bool: True if the event is affect relevant, False otherwise.
        """
        result = currentEvent != None

        for ex in self.affective_info.get_mood().affRevEventThreshold:
            result = result and self.affective_info.get_mood().is_affective_relevant(ex)

        return result

    def appraisal(self, event, concern_value, concerns):
        """
        This method is used to apply the appraisal process.

        Args:
            event (tuple): Event to be appraised.
            concern_value (float): Concern value of the event.

        Returns:
            bool: True if the event was appraised, False otherwise.
        """
        selectingCs = True
        result = False
        if event != None:
            # Calculating desirability
            if len(concerns):
                desirability = self.desirability(event, concerns)
                self.affective_info.get_appraisal_variables()[
                    "desirability"
                ] = desirability

            # Calculating likelihood.
            likelihood = self.likelihood(event)
            self.affective_info.get_appraisal_variables()["likelihood"] = likelihood

            # Calculating causal attribution
            causal_attribution = self.causalAttribution(event)
            self.affective_info.get_appraisal_variables()[
                "causal_attribution"
            ] = causal_attribution

            # Calculating controllability:
            if len(concerns):
                controllability = self.controllability(
                    event, concern_value, desirability
                )
                self.affective_info.get_appraisal_variables()[
                    "controllability"
                ] = controllability
                pass
            result = True
        else:
            self.affective_info.get_appraisal_variables()["desirability"] = None
            self.affective_info.get_appraisal_variables()["expectedness"] = None
            self.affective_info.get_appraisal_variables()["likelihood"] = None
            self.affective_info.get_appraisal_variables()["causal_attribution"] = None
            self.affective_info.get_appraisal_variables()["controllability"] = None
        return result

    def controllability(self, event, concernsValue, desirability):
        """
        This method is used to calculate the controllability of the event.

        Args:
            event (tuple): Event to be appraised.
            concernsValue (float): Concern value of the event.
            desirability (float): Desirability of the event.

        Returns:
            float: Controllability of the event.
        """
        result = None
        if desirability != None and concernsValue != None:
            result = desirability - concernsValue
            result = (result + 1) / 2
        return result

    def causalAttribution(self, event):
        """
        This method is used to calculate the causal attribution of the event.

        Args:
            event (tuple): Event to be appraised.

        Returns:
            str: Causal attribution of the event.
        """
        ca = None
        if any([annotation.functor == "source" for annotation in event[0].annots]):
            ca = "other"
        else:
            ca = "self"
        return ca

    def likelihood(self, event):
        """
        This method is used to calculate the likelihood of the event.

        Args:
            event (tuple): Event to be appraised.

        Returns:
            float: Likelihood of the event.
        """
        result = None
        if event != None and event[1].name == "addition":
            result = 1.0
        return result

    def expectedness(self, event, remove):
        """
        This method is used to calculate the expectedness of the event.

        Args:
            event (tuple): Event to be appraised.
            remove (bool): True if the event is removed, False otherwise.

        Returns:
            float: Expectedness of the event.
        """

        result1 = None
        result2 = None
        result = None

        if event != None:
            index = self.fulfilledExpectations.index(event[0])
            if index != -1:
                result1 = self.fulfilledExpectations[index][1]
                if remove:
                    self.fulfilledExpectations.pop(index)
            else:
                index = self.notFulfilledExpectations.index(event[0])
                if index != -1:
                    result1 = -1 * self.notFulfilledExpectations[index][1]
                    if remove:
                        self.notFulfilledExpectations.pop(index)

        # processing events that "didn't happen" and were expected in this affective cycle
        # Averaging negative expectedness and removing this value from the previous result
        av = 0
        count = 0
        for i in range(len(self.notFulfilledExpectations)):
            av = av + self.notFulfilledExpectations[i][1]
            count = count + 1
        if remove:
            self.notFulfilledExpectations = []
        if count > 0:
            result2 = av / count

        if result1 != None and result2 != None:
            result = max(-1, result1 - result2)

        return result  # range [-1,1]

    def desirability(self, event, concerns):
        """
        This method is used to calculate the desirability of the event.

        Args:
            event (tuple): Event to be appraised.

        Returns:
            float: Desirability of the event.
        """
        concernVal = None
        # This function return the first concern of the agent
        concern = concerns[("concern__", 1)][0]

        if concern != None:
            if event[1].name == "addition":
                # adding the new literal if the event is an addition of a belief
                concernVal = self.applyConcernForAddition(event, concern)
            else:
                concernVal = self.applyConcernForDeletion(event, concern)

            if concernVal != None:
                if float(concernVal) < 0 or float(concernVal) > 1:
                    concernVal = 0

        return float(concernVal)

    def update_affective_state(self):
        """
        This method is used to update the affective state.
        """
        current_mood: AffectiveState = self.affective_info.get_mood()

        self.affective_info.get_mood().update_affective_state(
            self.agent, self.affective_info, self.affective_categories
        )


class PairEventDesirability:
    def __init__(self, event):
        self.event = event
        self.av = {}
