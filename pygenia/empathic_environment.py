from __future__ import print_function

import copy
import time

import agentspeak
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util
from agentspeak.runtime import Agent, BuildTermVisitor, Intention

from agentspeak import UnaryOp
import pygenia.lexer
import pygenia.parser
import pygenia.stdlib
import pygenia.personality.personality
from pygenia.utils import (
    Instruction,
    BuildInstructionsVisitor,
    BuildQueryVisitor,
    TrueQuery,
)
from pygenia.affective_agent import AffectiveAgent
from pygenia.cognitive_engine.emotional_engine import Concern
import pygenia.environment
import pygenia.empathic_agent


LOGGER = agentspeak.get_logger(__name__)
C = {}


class EmpathicEnvironment(pygenia.environment.Environment):
    def build_agent_from_ast(
        self,
        source,
        ast_agent,
        actions,
        agent_cls=agentspeak.runtime.Agent,
        name=None,
        personality_cls=pygenia.personality.ocean_personality.OceanPersonality,
        em_engine_cls=pygenia.cognitive_engine.default_engine.DefaultEngine,
        affst_cls=pygenia.emotion_models.pad.PAD,
        affst_parameters=None,
    ):
        """
        This method is used to build the agent from the ast

        Returns:
            Tuple[ast_agent, Agent]: The ast of the agent and the agent

        """

        ast_agent, agent = pygenia.environment.Environment.build_agent_from_ast(
            self=self,
            source=source,
            ast_agent=ast_agent,
            actions=actions,
            agent_cls=agent_cls,
            name=name,
            personality_cls=personality_cls,
            em_engine_cls=em_engine_cls,
            affst_cls=affst_cls,
            affst_parameters=affst_parameters,
        )

        if isinstance(agent, pygenia.empathic_agent.EmpathicAgent):

            if ast_agent.others is not None:
                dict_others = {}
                for other in ast_agent.others.other_agents:
                    dict_others.setdefault(other, {})
                    for attribute in ast_agent.others.other_agents[other]:

                        term = agentspeak.evaluate(
                            ast_agent.others.other_agents[other][attribute], {}
                        )
                        if isinstance(term, agentspeak.parser.AstUnaryOp):
                            if term.operator == UnaryOp.op_neg:
                                dict_others[other].setdefault(
                                    attribute, term.operand.value * -1
                                )
                        else:
                            dict_others[other].setdefault(attribute, term.value)
                agent.set_others(dict_others)
            else:
                agent.set_others({})

        return ast_agent, agent

    def _build_agent(
        self,
        source,
        actions,
        agent_cls=agentspeak.runtime.Agent,
        name=None,
        personality_cls=pygenia.personality.ocean_personality.OceanPersonality,
        em_engine_cls=pygenia.cognitive_engine.default_engine.DefaultEngine,
        affst_cls=pygenia.emotion_models.pad.PAD,
        affst_parameters=None,
    ):
        # Parse source.
        log = agentspeak.Log(LOGGER, 3)
        tokens = pygenia.lexer.TokenStream(source, log)
        ast_agent = pygenia.parser.parse(source.name, tokens, log)
        log.throw()

        return self.build_agent_from_ast(
            source,
            ast_agent,
            actions,
            agent_cls,
            name,
            personality_cls,
            em_engine_cls,
            affst_cls,
            affst_parameters,
        )

    def build_agents(
        self,
        source,
        n,
        actions,
        agent_cls=Agent,
        name=None,
        personality_cls=pygenia.personality.ocean_personality.OceanPersonality,
        em_engine_cls=pygenia.cognitive_engine.default_engine.DefaultEngine,
        affst_cls=pygenia.emotion_models.pad.PAD,
        affst_parameters=None,
    ):
        if n <= 0:
            return []

        ast_agent, prototype_agent = self._build_agent(
            source,
            actions,
            agent_cls=agent_cls,
            personality_cls=personality_cls,
            em_engine_cls=em_engine_cls,
            affst_cls=affst_cls,
            affst_parameters=affst_parameters,
        )

        # Create more instances from the prototype, but with their own
        # callstacks. This is more efficient than making complete deep copies.
        agents = [prototype_agent]

        while len(agents) < n:
            agent = agent_cls(
                self,
                self._make_name(name or source.name),
                copy.copy(prototype_agent.beliefs),
                copy.copy(prototype_agent.rules),
                copy.copy(prototype_agent.plans),
            )

            for ast_goal in ast_agent.goals:
                term = ast_goal.atom.accept(BuildTermVisitor({}))
                agent.call(
                    agentspeak.Trigger.addition,
                    agentspeak.GoalType.achievement,
                    term,
                    Intention(),
                    delayed=True,
                )

            agents.append(agent)
            self.agents[agent.name] = agent

        return agents
