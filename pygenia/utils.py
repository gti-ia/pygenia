from __future__ import print_function

import copy
import functools

import agentspeak
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util

LOGGER = agentspeak.get_logger(__name__)
C = {}


class Instruction(agentspeak.runtime.Instruction):
    def __init__(
        self,
        f,
        loc=None,
        extra_locs=(),
        term=None,
        goal_type=None,
    ):
        super(Instruction, self).__init__(f, loc, extra_locs)
        self.term = term
        self.goal_type = goal_type


class TermQuery(agentspeak.runtime.TermQuery):

    def execute_concern(self, agent, intention, concern):
        # Boolean constants.
        term = agentspeak.evaluate(self.term, intention.scope)
        if term is True:
            yield
            return
        elif term is False:
            return

        choicepoint = object()

        concern = copy.deepcopy(concern)
        intention.stack.append(choicepoint)

        if agentspeak.unify(term, concern.head, intention.scope, intention.stack):
            for _ in concern.query.execute(agent, intention):
                yield

        agentspeak.reroll(intention.scope, intention.stack, choicepoint)


class BuildQueryVisitor(agentspeak.runtime.BuildQueryVisitor):

    def visit_literal(self, ast_literal):
        term = ast_literal.accept(agentspeak.runtime.BuildTermVisitor(self.variables))
        try:
            arity = len(ast_literal.terms)
            action_impl = self.actions.lookup(ast_literal.functor, arity)
            return ActionQuery(term, action_impl)
        except KeyError:
            if "." in ast_literal.functor:
                self.log.warning(
                    "no such action '%s/%d'",
                    ast_literal.functor,
                    arity,
                    loc=ast_literal.loc,
                    extra_locs=[t.loc for t in ast_literal.terms],
                )
            return agentspeak.runtime.TermQuery(term)


class TrueQuery(agentspeak.runtime.TrueQuery):
    def __str__(self):
        return "true"


class ActionQuery(agentspeak.runtime.ActionQuery):

    def execute(self, agent, intention):
        agent.circumstance.add_action((self.term, self.impl))
        """agent.C["A"] = (
            [(self.term, self.impl)]
            if "A" not in agent.C
            else agent.C["A"] + [(self.term, self.impl)]
        )"""

        for _ in self.impl(agent, self.term, intention):
            yield


class BuildInstructionsVisitor(agentspeak.runtime.BuildInstructionsVisitor):
    def add_instr(self, f, loc=None, extra_locs=(), term=None, goal_type=None):
        self.tail.success = Instruction(f, loc, extra_locs, term, goal_type)
        self.tail = self.tail.success
        return self.tail

    def visit_formula(self, ast_formula):
        if ast_formula.formula_type == agentspeak.FormulaType.add:
            term = ast_formula.term.accept(
                agentspeak.runtime.BuildTermVisitor(self.variables)
            )
            self.add_instr(
                functools.partial(agentspeak.runtime.add_belief, term),
                loc=ast_formula.loc,
                extra_locs=[ast_formula.term.loc],
            )
        elif ast_formula.formula_type == agentspeak.FormulaType.remove:
            term = ast_formula.term.accept(
                agentspeak.runtime.BuildTermVisitor(self.variables)
            )
            self.add_instr(functools.partial(agentspeak.runtime.remove_belief, term))
        elif ast_formula.formula_type == agentspeak.FormulaType.test:
            term = ast_formula.term.accept(
                agentspeak.runtime.BuildTermVisitor(self.variables)
            )
            self.add_instr(
                functools.partial(agentspeak.runtime.test_belief, term),
                loc=ast_formula.loc,
                extra_locs=[ast_formula.term.loc],
            )
        elif ast_formula.formula_type == agentspeak.FormulaType.replace:
            removal_term = ast_formula.term.accept(
                agentspeak.runtime.BuildReplacePatternVisitor()
            )
            self.add_instr(
                functools.partial(agentspeak.runtime.remove_belief, removal_term)
            )

            term = ast_formula.term.accept(
                agentspeak.runtime.BuildTermVisitor(self.variables)
            )
            self.add_instr(
                functools.partial(agentspeak.runtime.add_belief, term),
                loc=ast_formula.loc,
                extra_locs=[ast_formula.term.loc],
            )
        elif ast_formula.formula_type == agentspeak.FormulaType.achieve:
            term = ast_formula.term.accept(
                agentspeak.runtime.BuildTermVisitor(self.variables)
            )
            self.add_instr(
                functools.partial(
                    call,
                    agentspeak.Trigger.addition,
                    agentspeak.GoalType.achievement,
                    term,
                ),
                loc=ast_formula.loc,
                extra_locs=[ast_formula.term.loc],
                term=term,
                goal_type=agentspeak.GoalType.achievement,
            )
        elif ast_formula.formula_type == agentspeak.FormulaType.achieve_later:
            term = ast_formula.term.accept(
                agentspeak.runtime.BuildTermVisitor(self.variables)
            )
            self.add_instr(
                functools.partial(
                    agentspeak.runtime.call_delayed,
                    agentspeak.Trigger.addition,
                    agentspeak.GoalType.achievement,
                    term,
                ),
                loc=ast_formula.loc,
                extra_locs=[ast_formula.term.loc],
                term=term,
                goal_type=agentspeak.GoalType.achievement,
            )
        elif ast_formula.formula_type == agentspeak.FormulaType.term:
            query = ast_formula.term.accept(
                BuildQueryVisitor(self.variables, self.actions, self.log)
            )
            self.add_instr(functools.partial(agentspeak.runtime.push_query, query))
            self.add_instr(agentspeak.runtime.next_or_fail, loc=ast_formula.term.loc)
            self.add_instr(agentspeak.runtime.pop_query)

        return self.tail


def call(
    trigger: agentspeak.Trigger,
    goal_type: agentspeak.GoalType,
    term: agentspeak.Literal,
    agent: agentspeak.runtime.Agent,
    intention: agentspeak.runtime.Intention,
):
    """
    This method is used to call the agent

    Args:
        trigger (agentspeak.Trigger): The trigger of the agent
        goal_type (agentspeak.GoalType): The goal type of the agent
        term  (agentspeak.Literal): The term of the agent
        agent  (AffectiveAgent): The agent to call
        intention (agentspeak.runtime.Intention): The intention of the agent

    """
    return agent.call(trigger, goal_type, term, intention, delayed=False)
