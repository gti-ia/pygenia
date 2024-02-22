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
from pygenia.affective_agent import Concern, AffectiveAgent

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
        personality_cls=None,
        affst_cls=None,
        em_engine_cls=None,
    ):
        """
        This method is used to build the agent from the ast

        Returns:
            Tuple[ast_agent, Agent]: The ast of the agent and the agent

        """

        # agent_cls = AffectiveAgent

        log = agentspeak.Log(LOGGER, 3)
        agent = agent_cls(self, self._make_name(name or source.name))

        # Add personality and rationality level to agent prototype.
        if ast_agent.personality is not None:
            agent.personality.set_personality(
                personality_cls, ast_agent.personality.traits
            )
            agent.personality.set_rationality_level(
                ast_agent.personality.rationality_level
            )

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
            agent.current_step = "SelEv"
            term = ast_goal.atom.accept(agentspeak.runtime.BuildTermVisitor({}))
            f_event = agentspeak.runtime.Event(
                agentspeak.Trigger.addition, agentspeak.GoalType.achievement, term
            )
            agent.C["E"] = [f_event] if "E" not in agent.C else agent.C["E"] + [f_event]

        # Add rules to agent prototype.
        for concern in ast_agent.concerns:
            variables = {}
            head = concern.head.accept(agentspeak.runtime.BuildTermVisitor(variables))
            consequence = concern.consequence.accept(
                BuildQueryVisitor(variables, actions, log)
            )
            concern = Concern(head, consequence)
            agent.add_concern(concern)
            concern_value = agent.test_concern(
                head, agentspeak.runtime.Intention(), concern
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
        personality_cls=None,
        affst_cls=None,
        em_engine_cls=None,
    ):
        # Parse source.
        log = agentspeak.Log(LOGGER, 3)
        tokens = pygenia.lexer.TokenStream(source, log)
        ast_agent = pygenia.parser.parse(source.name, tokens, log)
        log.throw()

        return self.build_agent_from_ast(
            source, ast_agent, actions, agent_cls, name, personality_cls
        )

    def build_agents(
        self,
        source,
        n,
        actions,
        agent_cls=Agent,
        name=None,
        personality_cls=None,
        affst_cls=None,
        em_engine_cls=None,
    ):
        if n <= 0:
            return []

        ast_agent, prototype_agent = self._build_agent(
            source, actions, agent_cls=agent_cls, personality_cls=personality_cls
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