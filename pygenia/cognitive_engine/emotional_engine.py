from __future__ import print_function

import agentspeak
from pygenia.cognitive_engine.temporal_information import TemporalAffectiveInformation
from typing import Iterator
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util
from agentspeak import AslError, asl_str
from pygenia.utils import (
    TermQuery,
)
from pygenia.cognitive_engine.temporal_information import (
    TemporalAffectiveInformation,
)
from pygenia.cognitive_engine.circumstance import Circumstance


class EmotionalEngine:
    def __init__(self, agent, affst_cls):
        self.affective_info = TemporalAffectiveInformation(affst_cls)
        self.affective_categories = None
        self.event_queue = None
        self.concerns = None
        self.circumstance: Circumstance = None
        self.current_step_ast = None
        self.agent = agent
        self.affective_lavels = []
        self.concern_value = None

    def set_agent(self, agent):
        self.agent = agent

    def affective_transition_system(self):
        pass

    def isAffectRelevantEvent(self, event):
        pass

    def update_affective_state(self):
        pass

    def applyConcernForAddition(self, event, concern):
        """
        This method is used to apply the concern for the addition of a belief.

        Args:
            event (tuple): Event to be appraised.
            concern (Concern): Concern to be applied.

        Returns:
            float: Concern value of the event.
        """

        # We add the new belief to the agent's belief base, so we can calculate the concern value
        # self.add_belief(event[0], agentspeak.runtime.Intention().scope)
        # We calculate the concern value
        concern_value = self.test_concern(
            concern.head, agentspeak.runtime.Intention(), concern
        )
        # We remove the belief from the agent's belief base again
        # self.remove_belief(event[0], agentspeak.runtime.Intention())

        return concern_value

    def applyConcernForDeletion(self, event, concern):
        """
        This method is used to apply the concern for the deletion of a belief.

        Args:
            event (tuple): Event to be appraised.
            concern (Concern): Concern to be applied.

        Returns:
            float: Concern value of the event.
        """

        # We remove the belief from the agent's belief base, so we can calculate the concern value
        # self.remove_belief(event[0], agentspeak.runtime.Intention())
        # We calculate the concern value
        concern_value = self.test_concern(
            concern.head, agentspeak.runtime.Intention(), concern
        )
        # We add the belief to the agent's belief base again
        # self.add_belief(event[0], agentspeak.runtime.Intention())

        return concern_value

    def test_concern(self, term, intention, concern):
        """This function is used to know the value of a concern

        Args:
            term (Literal): Term of the concern
            intention (Intention): Intention of the agent
            concern (Concern): Concern of the agent

        Raises:
            AslError:  If the term is not a Literal

        Returns:
            OR[bool, str]: If the concern is not found, return False. If the concern is found, return the value of the concern
        """
        # print("--->>>>>", concern.query)
        # for x in concern.query:
        #    print("--->>>>>", x)
        term = agentspeak.evaluate(term, intention.scope)

        if not isinstance(term, agentspeak.Literal):
            raise AslError("expected concern literal, got: '%s'" % term)

        query = TermQuery(term)

        try:
            next(query.execute_concern(self.agent, intention, concern))
            concern_value = " ".join(
                asl_str(agentspeak.freeze(t, intention.scope, {})) for t in term.args
            )
            return concern_value
        except StopIteration:
            return False

    def set_event_queue(self, event_queue):
        self.event_queue = event_queue

    def set_concerns(self, concerns):
        self.concerns = concerns

    def set_circumstance(self, circumstance):
        self.circumstance = circumstance

    def waiters(self) -> Iterator[agentspeak.runtime.Waiter]:
        """
        This method is used to get the waiters of the intentions

        Returns:
            Iterator[agentspeak.runtime.Waiter]: The waiters of the intentions
        """
        return (
            intention[-1].waiter
            for intention in self.circumstance.get_intentions()
            if intention and intention[-1].waiter
        )

    def get_concern_value(self):
        print("---___", self.concern_value)
        return self.concern_value


class Concern:
    """
    This class is used to represent the concern of the agent
    """

    def __init__(self, head, query):
        self.head = head
        self.query = query
        self.predicates = None

    def __str__(self):
        return "%s :- %s" % (self.head, self.query)
