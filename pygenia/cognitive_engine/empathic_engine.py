from __future__ import print_function

import agentspeak
from pygenia.cognitive_engine.emotional_engine import EmotionalEngine
import random
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util
from pygenia.emotion_models.affective_state import AffectiveState
from pygenia.emotion_models.pa import Point


LOGGER = agentspeak.get_logger(__name__)
C = {}


class EmpathicEngine(EmotionalEngine):
    def __init__(self, agent, affst_cls):
        super().__init__(agent=agent, affst_cls=affst_cls)
        self.subject = None
        self.target = None
        self.interaction_value = None
        self.empathic_concern_value = None
        self.Mem = []
        self.empathic_emotions = []
        self.selected_emotions = []

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
            "EvClass": self.event_classification,
            "EmphAppr": self.empathic_appraisal,
            "EmphReg": self.empathic_regulation,
            "EmReg": self.emotion_regulation,
            "EmSel": self.emotion_selection,
            "Appr": self.applyAppraisal,
            "UpAs": self.applyUpdateAffState,
        }

        flag = True
        while flag == True and self.current_step_ast in options:
            flag = options[self.current_step_ast]()

        return True

    def event_classification(self) -> bool:
        self.event = None
        # self.concern_value = 0.0
        if True:  # while self.lock instead of True for the real implementation
            if self.event_queue:
                self.event = self.event_queue.pop()
                self.affective_info.set_event(self.event)
                self.subject = self.get_subject(self.event)
                self.target = self.get_target(self.event)
                self.interaction_value = self.get_interaction_value(self.event)
                if self.is_affective_relevant(self.event):
                    self.Mem.append(self.event)
                    if self.target not in ["self", None]:
                        self.agent.update_affective_link(
                            self.target, self.interaction_value
                        )
                        self.current_step_ast = "EmphAppr"
                    else:
                        if self.target == "self" and self.subject not in ["self", None]:
                            self.agent.update_affective_link(
                                self.subject, self.interaction_value
                            )
                        self.current_step_ast = "Appr"
                    return True
                else:
                    if self.target == "self" and self.subject not in ["self", None]:
                        self.agent.update_affective_link(
                            self.subject, self.interaction_value
                        )
                    return False
        return False

    def applyAppraisal(self) -> bool:
        """
        This method is used to apply the appraisal process.
        """
        # self.event = None
        # ped = PairEventDesirability(None)
        # if True:  # while self.lock instead of True for the real implementation
        #    if self.event_queue:
        #        ped.event = self.event_queue.pop()
        #        self.event = ped.event

        if self.event is None:
            self.appraisal(None, 0.0, self.concerns)
            self.currentEvent = None
            self.eventProcessedInCycle = False
        else:
            self.appraisal(self.event, self.concern_value, self.concerns)
            self.currentEvent = self.event
            self.eventProcessedInCycle = True

        # The next step is Update Aff State
        self.current_step_ast = "EmReg"
        return True

    def empathic_appraisal(self):
        affective_link = self.agent.get_other(self.target)["affective_link"]
        """
        self.empathic_concern_value = (
            self.concern_value
            * affective_link
            * self.agent.personality.get_empathic_level()
        )
        """
        self.empathic_concern_value = self.concern_value
        if self.event is None:
            self.appraisal(None, 0.0, self.concerns)
            self.currentEvent = None
            self.eventProcessedInCycle = False
        else:
            self.appraisal(self.event, self.empathic_concern_value, self.concerns)
            self.currentEvent = self.event
            self.eventProcessedInCycle = True
        self.current_step_ast = "EmphReg"
        return True

    def empathic_regulation(self):
        regulated_emotions = []
        affective_link = affective_link = self.agent.get_other(self.target)[
            "affective_link"
        ]
        for emotion in self.affective_info.get_elicited_emotions():
            regulated_emotion: Point = self.agent.personality.emotion_regulation(
                emotion
            )
            regulated_emotion.set_pleasure(
                regulated_emotion.get_pleasure()
                * affective_link
                * self.agent.personality.get_empathic_level()
            )
            regulated_emotion.set_arousal(
                regulated_emotion.get_arousal()
                * affective_link
                * self.agent.personality.get_empathic_level()
            )
            regulated_emotions.append(regulated_emotion)
        self.affective_info.set_elicited_emotions(regulated_emotions)
        self.current_step_ast = "EmSel"
        return True

    def emotion_regulation(self):
        regulated_emotions = []
        for emotion in self.affective_info.get_elicited_emotions():
            regulated_emotions.append(
                self.agent.personality.emotion_regulation(emotion)
            )
        self.affective_info.set_elicited_emotions(regulated_emotions)
        self.current_step_ast = "EmSel"
        return True

    def emotion_selection(self):
        self.selected_emotions = []
        for emotion in self.affective_info.get_elicited_emotions():
            self.selected_emotions.append(
                self.affective_info.get_mood().fuzzify_emotion(emotion)
            )
        self.current_step_ast = "UpAs"
        return True

    def applyUpdateAffState(self):
        """
        This method is used to update the affective state.
        """
        if self.eventProcessedInCycle:
            self.update_affective_state()
        return False

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

        self.affective_info.get_mood().estimate_emotion(self.affective_info)
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
        return self.concern_value

    def update_affective_state(self):
        """
        This method is used to update the affective state.
        """
        emotions = self.affective_info.get_elicited_emotions()
        self.affective_info.get_mood().update_affective_state(emotions)

    def estimate_concern_value(self, concerns, event):
        concernVal = None
        # This function return the first concern of the agent
        if len(concerns[("concern__", 1)]) == 0:
            return None

        concern = concerns[("concern__", 1)][0]

        if concern != None:
            if event[1].name == "addition":
                # adding the new literal if the event is an addition of a belief
                concernVal = self.applyConcernForAddition(event, concern)
            else:
                concernVal = self.applyConcernForDeletion(event, concern)

            if concernVal != None:
                concernVal = float(concernVal)
                if concernVal < 0:
                    concernVal = 0.0
                elif concernVal > 1:
                    concernVal = 1.0

        return concernVal

    def get_subject(self, event):
        return self.get_annotation_correspondence(event, "subject")

    def get_target(self, event):
        return self.get_annotation_correspondence(event, "target")

    def get_annotation_correspondence(self, event, correspondence):
        if event is not None:
            for annotation in event[0].annots:
                if annotation.functor == correspondence:
                    for subject in annotation.args:
                        if (
                            subject.functor == self.agent.name
                            or subject.functor == "self"
                        ):
                            return "self"
                    return annotation.args[0].functor
            return "self"
        return None

    def get_interaction_value(self, event):
        if event is not None:
            for annotation in event[0].annots:
                if annotation.functor == "interaction_value":
                    return annotation.args[0]
        return 0

    def is_affective_relevant(self, event) -> bool:
        if event is not None:
            if event[1] == agentspeak.Trigger.removal:
                return False
            self.concern_value = self.estimate_concern_value(self.concerns, event)
            if self.concern_value is not None:
                return True
            for annotation in event[0].annots:
                if annotation.functor == "affective_relevant":
                    return True
        return False

    def get_empathic_concern_value(self):
        return self.empathic_concern_value
