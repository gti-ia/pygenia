from __future__ import print_function

import copy
import time

import agentspeak
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util
from agentspeak.runtime import Agent, BuildTermVisitor, Intention


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
import pygenia.affective_agent
from pygenia.affective_agent import AffectiveAgent
from pygenia.cognitive_engine.emotional_engine import Concern

LOGGER = agentspeak.get_logger(__name__)
C = {}


class Environment(agentspeak.runtime.Environment):
    """
    This class is used to represent the environment of the agent

    Args:
        agentspeak.runtime.Environment: The environment of the agent defined in the agentspeak library
    """

    def ast_plan_body_visit(self, ast_plan, variables, actions, body, log):
        ast_plan.body.accept(BuildInstructionsVisitor(variables, actions, body, log))

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
        personality_emotion_matrix=None,
    ):
        """
        This method is used to build the agent from the ast

        Returns:
            Tuple[ast_agent, Agent]: The ast of the agent and the agent

        """

        # agent_cls = AffectiveAgent

        log = agentspeak.Log(LOGGER, 3)
        agent = agent_cls(self, self._make_name(name or source.name))

        if isinstance(agent, pygenia.affective_agent.AffectiveAgent):
            # Add personality and rationality level to agent prototype.
            agent.set_personality_emotion_matrix(personality_emotion_matrix)
            agent.set_emotional_engine(em_engine_cls, affst_cls)
            if affst_parameters is not None:
                agent.emotional_engine.affective_info.get_mood().init_parameters(
                    affst_parameters
                )
            else:
                agent.emotional_engine.affective_info.get_mood().init_parameters()
            agent.set_personality_cls(personality_cls)
            if ast_agent.personality is not None:
                agent.personality.set_personality(
                    attributes_dict=ast_agent.personality.traits,
                    parameters=affst_parameters,
                )
                if ast_agent.personality.rationality_level is not None:
                    agent.personality.set_rationality_level(
                        ast_agent.personality.rationality_level
                    )
                if ast_agent.personality.empathic_level is not None:
                    agent.personality.set_empathic_level(
                        ast_agent.personality.empathic_level
                    )
            else:
                agent.personality.set_personality(
                    attributes_dict={"O": 1, "C": 1, "E": 1, "A": 1, "N": 1},
                )
                agent.personality.set_rationality_level(0.5)
                agent.personality.set_empathic_level(0.5)

        # Add rules to agent prototype.
        for ast_rule in ast_agent.rules:
            variables = {}
            head = ast_rule.head.accept(agentspeak.runtime.BuildTermVisitor(variables))
            consequence = ast_rule.consequence.accept(
                BuildQueryVisitor(variables, actions, log)
            )
            rule = agentspeak.runtime.Rule(head, consequence)
            agent.add_rule(rule)

        # Add plans to agent prototype.
        for ast_plan in ast_agent.plans:
            variables = {}

            head = ast_plan.event.head.accept(
                agentspeak.runtime.BuildTermVisitor(variables)
            )

            if ast_plan.context:
                context = ast_plan.context.accept(
                    BuildQueryVisitor(variables, actions, log)
                )
            else:
                context = TrueQuery()

            body = Instruction(agentspeak.runtime.noop)
            body.f = agentspeak.runtime.noop
            if ast_plan.body:
                ast_plan.body.accept(
                    BuildInstructionsVisitor(variables, actions, body, log)
                )

            str_body = str(ast_plan.body)

            plan = agentspeak.runtime.Plan(
                ast_plan.event.trigger,
                ast_plan.event.goal_type,
                head,
                context,
                body,
                ast_plan.body,
                ast_plan.annotation,
            )

            if ast_plan.args[0] is not None:
                plan.args[0] = ast_plan.args[0]

            if ast_plan.args[1] is not None:
                plan.args[1] = ast_plan.args[1]

            agent.add_plan(plan)

        # Add beliefs to agent prototype.
        for ast_belief in ast_agent.beliefs:
            belief = ast_belief.accept(agentspeak.runtime.BuildTermVisitor({}))
            agent.call(
                agentspeak.Trigger.addition,
                agentspeak.GoalType.belief,
                belief,
                agentspeak.runtime.Intention(),
                delayed=True,
            )

        # Call initial goals on agent prototype. This is init of the reasoning cycle.
        # ProcMsg
        self.ast_agent = ast_agent

        for ast_goal in ast_agent.goals:
            # Start the first part of the reasoning cycle.
            if agent_cls == agentspeak.runtime.Agent:
                agent.current_step = "SelEv"
            else:
                agent.rational_cycle.set_current_step("SelEv")
            term = ast_goal.atom.accept(agentspeak.runtime.BuildTermVisitor({}))
            f_event = agentspeak.runtime.Event(
                agentspeak.Trigger.addition, agentspeak.GoalType.achievement, term
            )
            if agent_cls == agentspeak.runtime.Agent:
                agent.C["E"] = (
                    [f_event] if "E" not in agent.C else agent.C["E"] + [f_event]
                )
            else:
                agent.circumstance.add_event(f_event)
                # [f_event] if "E" not in agent.C else agent.C["E"] + [f_event]

        # Add rules to agent prototype.
        for concern in ast_agent.concerns:
            variables = {}
            head = concern.head.accept(agentspeak.runtime.BuildTermVisitor(variables))
            consequence = concern.consequence.accept(
                BuildQueryVisitor(variables, actions, log)
            )
            new_concern = Concern(head, consequence)
            new_concern.predicates = concern.predicates
            agent.add_concern(new_concern)
            concern_value = agent.emotional_engine.test_concern(
                head, agentspeak.runtime.Intention(), new_concern
            )

        # Report errors.
        log.throw()

        self.agents[agent.name] = agent
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
        personality_emotion_matrix=None,
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
            personality_emotion_matrix,
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
        personality_emotion_matrix=None,
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
            personality_emotion_matrix=personality_emotion_matrix,
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

    def run_agent(self, agent: AffectiveAgent):
        """
        This method is used to run the agent

        Args:
            agent (AffectiveAgent): The agent to run
        """
        more_work = True
        while more_work:
            # Start the second part of the reasoning cycle.
            agent.current_step = "SelInt"
            more_work = agent.step()
            if not more_work:
                # Sleep until the next deadline.
                wait_until = agent.shortest_deadline()
                if wait_until:
                    time.sleep(wait_until - self.time())
                    more_work = True

    def run(self):
        """
        This method is used to run the environment

        """
        maybe_more_work = True
        while maybe_more_work:
            maybe_more_work = False
            for agent in self.agents.values():
                if len(agent.circumstance.get_intentions()) > 0:
                    maybe_more_work = True
                if agent.run():
                    maybe_more_work = True
            if not maybe_more_work:
                deadlines = (
                    agent.shortest_deadline() for agent in self.agents.values()
                )
                deadlines = [deadline for deadline in deadlines if deadline is not None]
                if deadlines:
                    time.sleep(min(deadlines) - self.time())
                    maybe_more_work = True
