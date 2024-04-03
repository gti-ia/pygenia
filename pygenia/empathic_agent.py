from __future__ import print_function

import agentspeak
import pygenia.affective_agent
from pygenia.affective_agent import AffectiveAgent

LOGGER = agentspeak.get_logger(__name__)
C = {}


class EmpathicAgent(pygenia.affective_agent.AffectiveAgent):
    def __init__(
        self,
        env: agentspeak.runtime.Environment,
        name: str,
        beliefs=None,
        rules=None,
        plans=None,
        concerns=None,
        others=None,
    ):
        super(EmpathicAgent, self).__init__(env, name, beliefs, rules, plans, concerns)
        self.others = others

    def set_others(self, others):
        self.others = others

    def get_others(self):
        return self.others
