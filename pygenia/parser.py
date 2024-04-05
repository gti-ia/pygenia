# -*- coding: utf-8 -*-
#
# This file is part of the pygenia interpreter that extends the
# python-agentspeak interpreter (Copyright (C) 2016-2019 Niklas
# Fiekas <niklas.fiekas@tu-clausthal.de>.)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import errno
import os.path
import sys

import agentspeak
import agentspeak.util
from agentspeak import Trigger, GoalType, FormulaType, UnaryOp, BinaryOp
from agentspeak.parser import (
    AstNode,
    AstList,
    AstLinkedList,
    AstRule,
    AstGoal,
    AstFormula,
    AstConst,
    AstVariable,
    AstUnaryOp,
    AstBinaryOp,
)
from agentspeak.parser import (
    AstEvent,
    AstBody,
    AstWhile,
    AstFor,
    AstIfThenElse,
    FindVariablesVisitor,
    FindOpVisitor,
    NumericFoldVisitor,
)
from agentspeak.parser import BooleanFoldVisitor, TermFoldVisitor, LogicalFoldVisitor
from agentspeak.parser import (
    parse_list,
    parse_linked_list_tail,
    parse_atom,
    parse_power,
    parse_factor,
    parse_product,
    parse_arith_expr,
)
from agentspeak.parser import (
    parse_comparison,
    parse_not_expr,
    parse_and_expr,
    parse_term,
    parse_rule_or_belief,
    parse_initial_goal,
    parse_body,
)
from agentspeak.parser import (
    parse_while,
    parse_for,
    parse_if_then_else,
    parse_body_formula,
    parse_plan_body,
    parse_event,
    parse,
    validate,
    main,
    repl,
)


class AstBaseVisitor(object):
    def visit_literal(self, ast_literal):
        pass

    def visit_prob(self, ast_prob):
        pass

    def visit_list(self, ast_list):
        pass

    def visit_linked_list(self, ast_linked_list):
        pass

    def visit_rule(self, ast_rule):
        pass

    def visit_concern(self, ast_concern):
        pass

    def visit_goal(self, ast_goal):
        pass

    def visit_formula(self, ast_formula):
        pass

    def visit_const(self, ast_const):
        pass

    def visit_variable(self, ast_variable):
        pass

    def visit_unary_op(self, ast_unary_op):
        pass

    def visit_binary_op(self, ast_binary_op):
        pass

    def visit_plan(self, ast_plan):
        pass

    def visit_event(self, ast_event):
        pass

    def visit_body(self, ast_body):
        pass

    def visit_while(self, ast_while):
        pass

    def visit_for(self, ast_for):
        pass

    def visit_if_then_else(self, ast_if_then_else):
        pass

    def visit_agent(self, ast_agent):
        pass

    def visit_personality(self, ast_personality):
        pass


agentspeak.parser.AstBaseVisitor = AstBaseVisitor


class AstLiteral(AstNode):
    def __init__(self):
        super(AstLiteral, self).__init__()
        self.functor = None
        self.terms = []
        self.annotations = []
        self.time_range = None

    def accept(self, visitor):
        return visitor.visit_literal(self)

    def signature(self):
        return "%s/%d" % (self.functor, len(self.terms))

    def __str__(self):
        builder = []
        builder.append(self.functor)
        if self.terms:
            builder.append("(")
            builder.append(", ".join(str(term) for term in self.terms))
            builder.append(")")
        if self.annotations:
            builder.append("[")
            builder.append(", ".join(str(term) for term in self.annotations))
            builder.append("]")
        return "".join(builder)


agentspeak.parser.AstLiteral = AstLiteral


class AstTimePointRange(AstNode):
    def __init__(self):
        super(AstTimePointRange, self).__init__()
        self.functor = None
        self.start_range = None
        self.end_range = None

    def accept(self, visitor):
        return visitor.visit_time_point_range(self)

    def __str__(self):
        return "%s - %s" % (self.start_range, self.end_range)


class AstProb(AstNode):
    def __init__(self):
        super(AstProb, self).__init__()
        self.functor = None
        self.value_prob = None

    def accept(self, visitor):
        return visitor.visit_prob(self)

    def __str__(self):
        return "%s" % (self.value_prob)


class AstPlan(AstNode):
    def __init__(self):
        super(AstPlan, self).__init__()
        self.annotation = None
        self.annotation_terms = None
        self.event = None
        self.context = None
        self.body = None
        self.args = [None, None]

    def accept(self, visitor):
        return visitor.visit_plan(self)

    def signature(self):
        return self.event.signature()

    def __str__(self):
        builder = []

        if self.annotation is not None:
            builder.append("@")
            builder.append(str(self.annotation))
            builder.append("\n")

        builder.append(str(self.event))

        if self.context:
            builder.append(" : ")
            builder.append(str(self.context))

        if self.body:
            builder.append(" <-\n")
            builder.append(agentspeak.util.indent(str(self.body)))

        return "".join(builder)


agentspeak.parser.AstPlan = AstPlan


class AstAgent(AstNode):
    def __init__(self):
        super(AstAgent, self).__init__()
        self.rules = []
        self.beliefs = []
        self.goals = []
        self.plans = []
        self.concerns = []
        self.personality = None
        # self.others = None

    def accept(self, visitor):
        return visitor.visit_agent(self)

    def __str__(self):
        builder = []
        for rule in self.rules:
            if builder:
                builder.append("\n")
            builder.append(str(rule))
            builder.append(".")

        if self.beliefs:
            if builder:
                builder.append("\n")
            for belief in self.beliefs:
                if builder:
                    builder.append("\n")
                builder.append(str(belief))
                builder.append(".")

        if self.goals:
            if builder:
                builder.append("\n")
            for goal in self.goals:
                if builder:
                    builder.append("\n")
                builder.append(str(goal))
                builder.append(".")

        for plan in self.plans:
            if builder:
                builder.append("\n\n")
            builder.append(str(plan))
            builder.append(".")

        return "".join(builder)


agentspeak.parser.AstAgent = AstAgent


def parse_tkconcern(tok, tokens, log):
    literal = AstLiteral()
    literal.functor = tok.lexeme
    literal.loc = tok.loc

    tok = next(tokens)

    if tok.lexeme == "(":
        while True:
            tok = next(tokens)
            tok, term = parse_term(tok, tokens, log)
            literal.terms.append(term)
            if tok.lexeme == ")":
                tok = next(tokens)
                break
            elif tok.lexeme == ",":
                continue
            else:
                raise log.error(
                    "expected ')' or another argument for the literal, got '%s'",
                    tok.lexeme,
                    loc=tok.loc,
                    extra_locs=[literal.loc],
                )

    return tok, literal


def parse_literal(tok, tokens, log):
    if not tok.token.functor:
        raise log.error("expected functor, got '%s'", tok.lexeme, loc=tok.loc)

    literal = AstLiteral()
    literal.functor = tok.lexeme
    literal.loc = tok.loc

    tok = next(tokens)

    if tok.lexeme == "(":
        while True:
            tok = next(tokens)
            tok, term = parse_term(tok, tokens, log)
            literal.terms.append(term)
            if tok.lexeme == ")":
                tok = next(tokens)
                break
            elif tok.lexeme == ",":
                continue
            else:
                raise log.error(
                    "expected ')' or another argument for the literal, got '%s'",
                    tok.lexeme,
                    loc=tok.loc,
                    extra_locs=[literal.loc],
                )

    if tok.lexeme == "[":
        while True:
            tok = next(tokens)

            if tok.lexeme == "prob__":
                tok, prob = parse_prob(tok, tokens, log)

            else:
                tok, term = parse_term(tok, tokens, log)
                literal.annotations.append(term)

            if tok.lexeme == "]":
                tok = next(tokens)
                break
            elif tok.lexeme == ",":
                continue
            else:
                raise log.error(
                    "expected ']' or another annotation, got '%s'",
                    tok.lexeme,
                    loc=tok.loc,
                    extra_locs=[literal.loc],
                )

    if tok.lexeme == "<":
        tok, time_range = parse_time_point_range(tok, tokens, log)
        literal.time_range = time_range

    return tok, literal


agentspeak.parser.parse_literal = parse_literal


def parse_time_point_range(tok, tokens, log):
    time_range = AstTimePointRange()
    time_range.functor = tok.lexeme
    time_range.loc = tok.loc

    tok = next(tokens)
    tok, expr = parse_arith_expr(tok, tokens, log)
    time_range.start_range = expr

    if tok.lexeme == ",":
        tok = next(tokens)
    else:
        raise log.error(
            "expected ',', got '%s'",
            tok.lexeme,
            loc=tok.loc,
            extra_locs=[time_range.loc],
        )

    tok, expr = parse_arith_expr(tok, tokens, log)
    time_range.end_range = expr

    if tok.lexeme == ">":
        tok = next(tokens)
    else:
        raise log.error(
            "expected '>', got '%s'",
            tok.lexeme,
            loc=tok.loc,
            extra_locs=[time_range.loc],
        )

    return tok, time_range


def parse_prob(tok, tokens, log):
    prob = AstProb()
    prob.functor = tok.lexeme
    prob.loc = tok.loc

    tok = next(tokens)

    if tok.lexeme == ":":
        tok = next(tokens)
    else:
        raise log.error(
            "expected ':', got '%s'", tok.lexeme, loc=tok.loc, extra_locs=[prob.loc]
        )

    tok, prob.value_prob = parse_arith_expr(tok, tokens, log)

    return tok, prob


def parse_concern(tok, tokens, log):
    if "." in tok.lexeme:
        log.warning(
            "found '.' in assertion. should this have been an action?", loc=tok.loc
        )

    tok, belief_atom = parse_tkconcern(tok, tokens, log)

    if tok.lexeme == ":-":
        # A rule with head and body.
        concern = AstConcern()
        concern.head = belief_atom
        concern.loc = tok.loc

        tok = next(tokens)
        tok, concern.consequence = parse_term(tok, tokens, log)
        return tok, concern
    else:
        # Just the belief atom.
        return tok, belief_atom


def parse_personality(tok, tokens, log):
    personality = AstPersonality()
    personality.loc = tok.loc

    tok = next(tokens)
    if tok.lexeme == ":":
        tok = next(tokens)
    else:
        raise log.error("expected :, got '%s'", tok.lexeme, loc=tok.loc)

    if tok.lexeme != "{":
        raise log.error("expected {, got '%s'", tok.lexeme, loc=tok.loc)

    personality.traits = parse_personality_traits_array(tok, tokens, log)

    tok = next(tokens)

    if tok.lexeme == ",":
        tok = next(tokens)
        try:
            rl = float(tok.lexeme)
            personality.rationality_level = rl
            tok = next(tokens)
        except:
            raise log.error(
                "expected a number value, got '%s'", tok.lexeme, loc=tok.loc
            )

    if tok.lexeme != "}":
        raise log.error("expected }, got '%s'", tok.lexeme, loc=tok.loc)

    tok = next(tokens)

    return tok, personality


def parse_personality_traits_array(tok, tokens, log):
    traits = {}

    tok = next(tokens)

    if tok.lexeme != "[":
        raise log.error("expected [, got '%s'", tok.lexeme, loc=tok.loc)

    tok = next(tokens)

    while tok.lexeme != "]":
        tok, trait, value = parse_personality_trait(tok, tokens, log)
        traits[trait] = value
        if tok.lexeme == ",":
            tok = next(tokens)

    return traits


def parse_personality_trait(tok, tokens, log):
    trait = tok.lexeme
    tok = next(tokens)

    if tok.lexeme != ":":
        raise log.error("expected :, got '%s'", tok.lexeme, loc=tok.loc)

    tok = next(tokens)

    try:
        value = float(tok.lexeme)
    except:
        raise log.error(
            "expected a float value for the personality trait '%s', got '%s'",
            trait,
            tok.lexeme,
            loc=tok.loc,
        )

    tok = next(tokens)

    return tok, trait, value


def parse_others(tok, tokens, log):
    others = AstOthers()
    others.loc = tok.loc
    # id = ''
    tok = next(tokens)
    if tok.lexeme == ":":
        tok = next(tokens)
    else:
        raise log.error("expected :, got '%s'", tok.lexeme, loc=tok.loc)

    tok, others.other_agents = parse_others_list(tok, tokens, log)

    """if tok.lexeme == "{":
        tok = next(tokens)
    else:
        raise log.error("expected {, got '%s'", tok.lexeme, loc=tok.loc)
    
    if tok.token.functor:
        id = tok.lexeme
        others.other_agents.setdefault(id,[])
        tok = next(tokens)
    else: 
        raise log.error("expected functor, got '%s'", tok.lexeme, loc=tok.loc)
    
    if tok.lexeme == ":":
        tok = next(tokens)
    else:
        raise log.error("expected :, got '%s'", tok.lexeme, loc=tok.loc)
    
    tok, others.other_agents[id] = parse_others_array(tok, tokens, log)
    
    if tok.lexeme != "}":
        raise log.error("expected }, got '%s'", tok.lexeme, loc=tok.loc)"""

    tok = next(tokens)

    return tok, others


def parse_others_list(tok, tokens, log):
    others_list = {}
    if tok.lexeme == "{":
        tok = next(tokens)
    else:
        raise log.error("expected {, got '%s'", tok.lexeme, loc=tok.loc)

    if tok.lexeme == "}":
        return tok, others_list

    if tok.token.functor:
        id = tok.lexeme
        others_list.setdefault(id, [])
        tok = next(tokens)
    else:
        raise log.error("expected functor, got '%s'", tok.lexeme, loc=tok.loc)

    if tok.lexeme == ":":
        tok = next(tokens)
    else:
        raise log.error("expected :, got '%s'", tok.lexeme, loc=tok.loc)

    tok, others_list[id] = parse_others_array(tok, tokens, log)

    while tok.lexeme != "}":
        if tok.lexeme == ",":
            tok = next(tokens)
        else:
            raise log.error("expected ',', got '%s'", tok.lexeme, loc=tok.loc)

        if tok.token.functor:
            id = tok.lexeme
            others_list.setdefault(id, [])
            tok = next(tokens)
        else:
            raise log.error("expected functor, got '%s'", tok.lexeme, loc=tok.loc)

        if tok.lexeme == ":":
            tok = next(tokens)
        else:
            raise log.error("expected :, got '%s'", tok.lexeme, loc=tok.loc)

        tok, others_list[id] = parse_others_array(tok, tokens, log)

    return tok, others_list


def parse_others_array(tok, tokens, log):
    others_array = {}

    if tok.lexeme == "[":
        tok = next(tokens)
    else:
        raise log.error("expected [, got '%s'", tok.lexeme, loc=tok.loc)

    tok, id, value = parse_other_parameters(tok, tokens, log)
    others_array.setdefault(id, value)

    while tok.lexeme != "]":
        if tok.lexeme == ",":
            tok = next(tokens)
        else:
            raise log.error("expected ',', got '%s'", tok.lexeme, loc=tok.loc)

        tok, id, value = parse_other_parameters(tok, tokens, log)
        others_array.setdefault(id, value)

    tok = next(tokens)
    return tok, others_array


def parse_other_parameters(tok, tokens, log):
    if tok.token.functor:
        id = tok.lexeme
        tok = next(tokens)
    else:
        raise log.error("expected functor, got '%s'", tok.lexeme, loc=tok.loc)

    if tok.lexeme == ":":
        tok = next(tokens)
    else:
        raise log.error("expected :, got '%s'", tok.lexeme, loc=tok.loc)

    tok, value = parse_arith_expr(tok, tokens, log)

    return tok, id, value


def parse_plan(tok, tokens, log):
    plan = AstPlan()
    if tok.lexeme == "@":
        tok = next(tokens)

        tok, annotation = parse_literal(tok, tokens, log)
        plan.annotation = annotation
        plan.annotation_terms = annotation.annotations

    tok, event = parse_event(tok, tokens, log)
    plan.event = event
    plan.loc = event.loc

    # If we find a () in the event this indicate that the trigger plan have arguments, we save them in plan.args[0]
    if "(" in str(event):
        plan.args[0] = str(event).split("(")[1].split(")")[0]

    # If we find a [] in the event this indicate that the trigger plan have annotations, we save them in plan.args[1]
    if "[" in str(event):
        plan.args[1] = str(event).split("[")[1].split("]")[0]

    if tok.lexeme == ":":
        tok = next(tokens)
        tok, plan.context = parse_term(tok, tokens, log)

    if tok.lexeme == "<-":
        body_loc = tok.loc
        tok = next(tokens)
        tok, plan.body = parse_plan_body(tok, tokens, log)
        plan.body.loc = body_loc

    return tok, plan


agentspeak.parser.parse_plan = parse_plan


class AstConcern(AstNode):
    def __init__(self):
        super(AstConcern, self).__init__()
        self.head = None
        self.consequence = None

    def accept(self, visitor):
        return visitor.visit_concern(self)

    def __str__(self):
        return "%s :- %s" % (self.head, self.consequence)


class AstPersonality(AstNode):
    def __init__(self):
        super(AstPersonality, self).__init__()
        self.traits = {}
        self.rationality_level = None

    def accept(self, visitor):
        return visitor.visit_personality(self)

    def __str__(self):
        return "%s :- %s, %s" % ("personality", self.traits, self.rationality_level)


class AstOthers(AstNode):
    def __init__(self):
        super(AstOthers, self).__init__()
        self.other_agents = {}

    def accept(self, visitor):
        return visitor.visit_others(self)

    def __str__(self):
        builder = []
        if self.other_agents:
            builder.append("[")
            builder.append(
                ", ".join(str(f"{agent.name}: {agent}") for agent in self.other_agents)
            )
            builder.append("]")
        return "".join(builder)


class AstOtherAgent(AstNode):
    def __init__(self):
        super(AstOtherAgent, self).__init__()
        self.name = None
        self.information = None

    def accept(self, visitor):
        return visitor.visit_other_agent(self)

    def __str__(self):
        builder = []
        if self.information:
            builder.append("[")
            builder.append(
                ", ".join(
                    str(f"{info}: {self.information[info]}")
                    for info in self.information
                )
            )
            builder.append("]")
        return "".join(builder)


def parse_agent(filename, tokens, log, included_files, directive=None):
    included_files = included_files | frozenset([os.path.normpath(filename)])
    agent = AstAgent()
    last_plan = None

    while True:
        try:
            tok = next(tokens)
        except StopIteration:
            if directive:
                # TODO: Where was the directive started?
                raise log.error(
                    "end of file, but did not close directive '%s'", directive
                )
            return validate(agent, log)

        if tok.lexeme == "{":
            tok = next(tokens)
            if tok.lexeme == "include":
                include_loc = tok.loc
                tok = next(tokens)
                if tok.lexeme != "(":
                    raise log.error(
                        "expected '(' after include, got '%s'",
                        tok.lexeme,
                        loc=tok.loc,
                        extra_locs=[include_loc],
                    )
                tok = next(tokens)
                if not tok.token.string:
                    raise log.error(
                        "expected filename to include, got '%s'",
                        tok.lexeme,
                        loc=tok.loc,
                        extra_locs=[include_loc],
                    )
                include = agentspeak.parse_string(tok.lexeme)
                tok = next(tokens)
                if tok.lexeme != ")":
                    raise log.error(
                        "expected ')' after include filename, got '%s'",
                        tok.lexeme,
                        loc=tok.loc,
                        extra_locs=[include_loc],
                    )
                tok = next(tokens)
                if tok.lexeme != "}":
                    raise log.error(
                        "expected '}' to close include directive, got '%s'",
                        tok.lexeme,
                        loc=tok.loc,
                        extra_locs=[include_loc],
                    )

                # Resolve included path.
                include = os.path.join(os.path.dirname(filename), include)

                # Parse included file.
                if include in included_files:
                    log.error(
                        "infinite recursive include: '%s'", include, loc=include_loc
                    )
                else:
                    try:
                        included_file = open(include)
                    except IOError as err:
                        if err.errno == errno.ENOENT:
                            log.error(
                                "include file not found: '%s'", include, loc=include_loc
                            )
                        else:
                            raise
                    else:
                        included_tokens = agentspeak.lexer.TokenStream(included_file, 1)
                        included_agent = parse(
                            include, included_tokens, log, included_files
                        )
                        agent.beliefs += included_agent.beliefs
                        agent.rules += included_agent.rules
                        agent.goals += included_agent.goals
                        agent.plans += included_agent.plans
                        included_file.close()
            elif tok.lexeme == "begin":
                begin_loc = tok.loc
                tok = next(tokens)
                tok, sub_directive = parse_literal(tok, tokens, log)
                if tok.lexeme != "}":
                    raise log.error(
                        "expected '}' after begin, got '%s'",
                        tok.lexeme,
                        loc=tok.loc,
                        extra_locs=[begin_loc],
                    )
                log.warning("directives are ignored as of yet", loc=sub_directive.loc)
                sub_agent = parse(filename, tokens, log, included_files, sub_directive)
                agent.beliefs += sub_agent.beliefs
                agent.rules += sub_agent.rules
                agent.goals += sub_agent.goals
                agent.plans += sub_agent.plans
            elif tok.lexeme == "end":
                end_loc = tok.loc
                tok = next(tokens)
                if tok.lexeme != "}":
                    raise log.error(
                        "expected '}' after end, got '%s'",
                        tok.lexeme,
                        loc=tok.loc,
                        extra_locs=[end_loc],
                    )
                if not directive:
                    log.error("unexpected end", loc=end_loc)
                else:
                    return validate(agent, log)
            else:
                raise log.error(
                    "expected 'include', or 'begin' or 'end' after '{', got '%s'",
                    tok.lexeme,
                    loc=tok.loc,
                )
        # TK CONCERN
        elif tok.token.concern:
            tok, ast_node = parse_concern(tok, tokens, log)
            if isinstance(ast_node, AstConcern):
                if tok.lexeme != ".":
                    log.info("missing '.' after this concern", loc=ast_node.loc)
                    raise log.error(
                        "expected '.' after concern, got '%s'",
                        tok.lexeme,
                        loc=tok.loc,
                        extra_locs=[ast_node.loc],
                    )
                agent.concerns.append(ast_node)
        elif tok.token.personality:
            # TK PERSONALITY
            tok, ast_node = parse_personality(tok, tokens, log)
            if isinstance(ast_node, AstPersonality):
                agent.personality = ast_node
        elif tok.token.others:
            # TK OTHERS
            tok, ast_node = parse_others(tok, tokens, log)
            if isinstance(ast_node, AstOthers):
                agent.others = ast_node
        elif tok.token.functor:
            if last_plan is not None:
                log.warning(
                    "assertion after plan. should this have been part of '%s'?",
                    last_plan.signature(),
                    loc=tok.loc,
                )
            tok, ast_node = parse_rule_or_belief(tok, tokens, log)
            if isinstance(ast_node, AstRule):
                if tok.lexeme != ".":
                    log.info("missing '.' after this rule", loc=ast_node.loc)
                    raise log.error(
                        "expected '.' after rule, got '%s'",
                        tok.lexeme,
                        loc=tok.loc,
                        extra_locs=[ast_node.loc],
                    )
                agent.rules.append(ast_node)
            else:
                if tok.lexeme != ".":
                    log.info("missing '.' after this belief", loc=ast_node.loc)
                    raise log.error(
                        "expected '.' after belief, got '%s'",
                        tok.lexeme,
                        loc=tok.loc,
                        extra_locs=[ast_node.loc],
                    )
                agent.beliefs.append(ast_node)
        elif tok.lexeme == "!":
            tok, ast_node = parse_initial_goal(tok, tokens, log)
            if tok.lexeme != ".":
                log.info("missing '.' after this goal", loc=ast_node.loc)
                raise log.error(
                    "expected '.' after initial goal, got '%s'",
                    tok.lexeme,
                    loc=tok.loc,
                    extra_locs=[ast_node.loc],
                )
            agent.goals.append(ast_node)
        elif tok.lexeme in ["@", "+", "-"]:
            tok, last_plan = parse_plan(tok, tokens, log)

            if tok.lexeme != ".":
                log.info("missing '.' after this plan", loc=last_plan.loc)
                raise log.error(
                    "expected '.' after plan, got '%s'",
                    tok.lexeme,
                    loc=tok.loc,
                    extra_locs=[last_plan.loc],
                )
            agent.plans.append(last_plan)
        else:
            log.error("unexpected token: '%s'", tok.lexeme, loc=tok.loc)


agentspeak.parser.parse_agent = parse_agent


class ConstFoldVisitor(object):
    def __init__(self, log):
        self.log = log

    def visit_binary_op(self, ast_binary_op):
        return ast_binary_op.accept(TermFoldVisitor(self.log))

    def visit_unary_op(self, ast_unary_op):
        return ast_unary_op.accept(TermFoldVisitor(self.log))

    def visit_agent(self, ast_agent):
        ast_agent.rules = [rule.accept(self) for rule in ast_agent.rules]
        ast_agent.beliefs = [belief.accept(self) for belief in ast_agent.beliefs]
        ast_agent.goals = [goal.accept(self) for goal in ast_agent.goals]
        ast_agent.plans = [plan.accept(self) for plan in ast_agent.plans]
        return ast_agent

    def visit_if_then_else(self, ast_if_then_else):
        ast_if_then_else.condition = ast_if_then_else.condition.accept(
            LogicalFoldVisitor(self.log)
        )
        ast_if_then_else.if_body = ast_if_then_else.if_body.accept(self)
        ast_if_then_else.else_body = (
            ast_if_then_else.else_body.accept(self)
            if ast_if_then_else.else_body
            else None
        )
        return ast_if_then_else

    def visit_for(self, ast_for):
        ast_for.generator = ast_for.generator.accept(LogicalFoldVisitor(self.log))
        ast_for.body = ast_for.body.accept(self)
        return ast_for

    def visit_while(self, ast_while):
        ast_while.condition = ast_while.condition.accept(LogicalFoldVisitor(self.log))
        ast_while.body = ast_while.body.accept(self)
        return ast_while

    def visit_body(self, ast_body):
        ast_body.formulas = [formula.accept(self) for formula in ast_body.formulas]
        return ast_body

    def visit_event(self, ast_event):
        ast_event.head = ast_event.head.accept(TermFoldVisitor(self.log))
        return ast_event

    def visit_plan(self, ast_plan):
        if ast_plan.annotation is not None:
            ast_plan.annotation = ast_plan.annotation.accept(TermFoldVisitor(self.log))

        ast_plan.event = ast_plan.event.accept(self)
        ast_plan.context = (
            ast_plan.context.accept(LogicalFoldVisitor(self.log))
            if ast_plan.context
            else None
        )
        ast_plan.body = ast_plan.body.accept(self) if ast_plan.body else None
        return ast_plan

    def visit_variable(self, ast_variable):
        return ast_variable

    def visit_const(self, ast_const):
        return ast_const

    def visit_formula(self, ast_formula):
        if ast_formula.formula_type == FormulaType.term:
            ast_formula.term = ast_formula.term.accept(LogicalFoldVisitor(self.log))
        else:
            if isinstance(ast_formula.term, (AstLiteral, AstVariable)):
                ast_formula.term = ast_formula.term.accept(TermFoldVisitor(self.log))
            else:
                self.log.error(
                    "expected literal or variable after '%s'",
                    ast_formula.formula_type,
                    loc=ast_formula.loc,
                    extra_locs=[ast_formula.term.loc],
                )

        return ast_formula

    def visit_goal(self, ast_goal):
        ast_goal.atom = ast_goal.atom.accept(TermFoldVisitor(self.log))
        return ast_goal

    def visit_rule(self, ast_rule):
        ast_rule.head = ast_rule.head.accept(TermFoldVisitor(self.log))
        ast_rule.consequence = ast_rule.consequence.accept(LogicalFoldVisitor(self.log))
        return ast_rule

    def visit_concern(self, ast_concern):
        ast_concern.head = ast_concern.head.accept(TermFoldVisitor(self.log))
        ast_concern.consequence = ast_concern.consequence.accept(
            LogicalFoldVisitor(self.log)
        )
        return ast_concern

    def visit_others(self, ast_others):
        return ast_others

    def visit_other_agent(self, ast_other_agent):
        return ast_other_agent

    def visit_list(self, ast_list):
        term_visitor = TermFoldVisitor(self.log)
        ast_list.terms = [term.accept(term_visitor) for term in ast_list.terms]
        return ast_list

    def visit_literal(self, ast_literal):
        term_visitor = TermFoldVisitor(self.log)
        ast_literal.terms = [term.accept(term_visitor) for term in ast_literal.terms]
        ast_literal.annotations = [
            annotation.accept(term_visitor) for annotation in ast_literal.annotations
        ]
        return ast_literal


agentspeak.parser.ConstFoldVisitor = ConstFoldVisitor


if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        if args:
            for arg in args:
                with open(arg) as source:
                    main(source, print)
        elif sys.stdin.isatty():
            repl(print)
        else:
            main(sys.stdin, print)
    except agentspeak.AggregatedError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
