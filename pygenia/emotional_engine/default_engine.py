from __future__ import print_function

import collections
import math
import agentspeak
from pygenia.emotional_engine.as_utils import TemporalAffectiveInformation
from pygenia.emotional_engine.emotional_engine import EmotionalEngine
import asyncio
import random
from enum import Enum
from typing import Iterator
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util
import numpy as np
from agentspeak import AslError, asl_str
import pygenia.personality.personality
from pygenia.utils import (
    TermQuery,
    TrueQuery,
    Instruction,
    BuildInstructionsVisitor,
    BuildQueryVisitor,
)
from pygenia.emotional_engine.as_utils import TemporalAffectiveInformation
from pygenia.affective_state.pad import PAD
from pygenia.affective_agent import AffectiveAgent

LOGGER = agentspeak.get_logger(__name__)
C = {}


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
        self.T = {"p": None, "Ap": [], "i": None, "R": [], "e": None}

    def call(
        self,
        agent: AffectiveAgent,
        trigger: agentspeak.Trigger,
        goal_type: agentspeak.GoalType,
        term: agentspeak.Literal,
        calling_intention: agentspeak.runtime.Intention,
        delayed: bool = False,
    ):
        """This method is used to call an event.

        Args:
            trigger (agentspeak.Trigger): Trigger of the event.
            goal_type (agentspeak.GoalType): Type of the event.
            term (agentspeak.Literal): Term of the event.
            calling_intention (agentspeak.runtime.Intention): Intention of the agent.
            delayed (bool, optional): Delayed event. Defaults to False.

        Raises:
            AslError: "expected literal" if the term is not a literal.
            AslError: "expected literal term" if the term is not a literal term.
            AslError: "no applicable plan for" + str(term)" if there is no applicable plan for the term.
            log.error: "expected end of plan" if the plan is not finished. The plan finish with a ".".

        Returns:
            bool: True if the event is called.

        If the event is a belief, we add or remove it.

        If the event is a goal addition, we start the reasoning cycle.

        If the event is a goal deletion, we remove it from the intentions queue.

        If the event is a tellHow addition, we tell the agent how to do it.

        If the event is a tellHow deletion, we remove the tellHow from the agent.

        If the event is a askHow addition, we ask the agent how to do it.
        """
        # Modify beliefs.
        if goal_type == agentspeak.GoalType.belief:
            # We recieve a belief and the affective cycle is activated.
            # We need to provide to the sunction the term and the Trigger type.
            agent.event_queue.append((term, trigger))
            # self.appraisal((term, trigger),0)
            if trigger == agentspeak.Trigger.addition:
                agent.add_belief(term, calling_intention.scope)
            else:
                found = agent.remove_belief(term, calling_intention)
                if not found:
                    return True

        # Freeze with caller scope.
        frozen = agentspeak.freeze(term, calling_intention.scope, {})

        if not isinstance(frozen, agentspeak.Literal):
            raise AslError("expected literal")

        # Wake up waiting intentions.
        for intention_stack in self.circunstance["I"]:
            if not intention_stack:
                continue
            intention = intention_stack[-1]

            if not intention.waiter or not intention.waiter.event:
                continue
            event = intention.waiter.event

            if event.trigger != trigger or event.goal_type != goal_type:
                continue

            if agentspeak.unifies_annotated(event.head, frozen):
                intention.waiter = None

        # If the goal is an achievement and the trigger is an removal, then the agent will delete the goal from his list of intentions
        if (
            goal_type == agentspeak.GoalType.achievement
            and trigger == agentspeak.Trigger.removal
        ):
            if not agentspeak.is_literal(term):
                raise AslError("expected literal term")

            # Remove a intention passed by the parameters.
            for intention_stack in self.circunstance["I"]:
                if not intention_stack:
                    continue

                intention = intention_stack[-1]

                if intention.head_term.functor == term.functor:
                    if agentspeak.unifies(term.args, intention.head_term.args):
                        intention_stack.remove(intention)
            return True

        # If the goal is an tellHow and the trigger is an addition, then the agent will add the goal received as string to his list of plans
        if (
            goal_type == agentspeak.GoalType.tellHow
            and trigger == agentspeak.Trigger.addition
        ):

            str_plan = term.args[2]

            tokens = []
            tokens.extend(
                agentspeak.lexer.tokenize(
                    agentspeak.StringSource("<stdin>", str_plan),
                    agentspeak.Log(LOGGER),
                    1,
                )
            )  # extend the tokens with the tokens of the string plan

            # Prepare the conversion from tokens to AstPlan
            first_token = tokens[0]
            log = agentspeak.Log(LOGGER)
            tokens.pop(0)
            tokens = iter(tokens)

            # Converts the list of tokens to a Astplan
            if first_token.lexeme in ["@", "+", "-"]:
                tok, ast_plan = agentspeak.parser.parse_plan(first_token, tokens, log)
                if tok.lexeme != ".":
                    raise log.error("", tok, "expected end of plan")

            # Prepare the conversión of Astplan to Plan
            variables = {}
            actions = agentspeak.stdlib.actions

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

            # Converts the Astplan to Plan
            plan = agentspeak.runtime.Plan(
                ast_plan.event.trigger,
                ast_plan.event.goal_type,
                head,
                context,
                body,
                ast_plan.body,
                ast_plan.annotations,
            )

            if ast_plan.args[0] is not None:
                plan.args[0] = ast_plan.args[0]

            if ast_plan.args[1] is not None:
                plan.args[1] = ast_plan.args[1]

            # Add the plan to the agent
            agent.add_plan(plan)
            return True

        # If the goal is an askHow and the trigger is an addition, then the agent will find the plan in his list of plans and send it to the agent that asked
        if (
            goal_type == agentspeak.GoalType.askHow
            and trigger == agentspeak.Trigger.addition
        ):
            self.T["e"] = agentspeak.runtime.Event(trigger, goal_type, term.args[2])
            return agent._ask_how(term)

        # If the goal is an unTellHow and the trigger is a removal, then the agent will delete the goal from his list of plans
        if (
            goal_type == agentspeak.GoalType.tellHow
            and trigger == agentspeak.Trigger.removal
        ):

            label = term.args[2]

            delete_plan = []
            plans = agent.plans.values()
            for plan in plans:
                for differents in plan:
                    if ("@" + str(differents.annotation[0].functor)).startswith(label):
                        delete_plan.append(differents)
            for differents in delete_plan:
                plan.remove(differents)
            return True

        self.circunstance["E"] = (
            [agentspeak.runtime.Event(trigger, goal_type, term)]
            if "E" not in self.circunstance
            else self.circunstance["E"]
            + [agentspeak.runtime.Event(trigger, goal_type, term)]
        )
        self.current_step = "SelEv"
        self.applySemanticRuleDeliberate(delayed, calling_intention)

        # if goal_type == agentspeak.GoalType.achievement and trigger == agentspeak.Trigger.addition:
        #    raise AslError("no applicable plan for %s%s%s/%d" % (
        #        trigger.value, goal_type.value, frozen.functor, len(frozen.args)))
        # elif goal_type == agentspeak.GoalType.test:
        #    return self.test_belief(term, calling_intention)
        return True

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
