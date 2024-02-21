from __future__ import print_function

import asyncio
import collections
import math
import random
from enum import Enum
from typing import Iterator

import agentspeak
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util
import numpy as np
from agentspeak import AslError, asl_str


import pygenia.lexer
import pygenia.parser
import pygenia.stdlib
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

LOGGER = agentspeak.get_logger(__name__)
C = {}


class AffectiveAgent(agentspeak.runtime.Agent):
    """
    This class is a subclass of the Agent class.
    It is used to add the affective layer to the agent.
    """

    def __init__(
        self,
        env: agentspeak.runtime.Environment,
        name: str,
        beliefs=None,
        rules=None,
        plans=None,
        concerns=None,
    ):
        """
        Constructor of the AffectiveAgent class.

        Args:
            env (agentspeak.runtime.Environment): Environment of the agent.
            name (str): Name of the agent.
            beliefs (dict): Beliefs of the agent.
            rules (dict): Rules of the agent.
            plans (dict): Plans of the agent.

        Attributes:
            env (agentspeak.runtime.Environment): Environment of the agent.
            name (str): Name of the agent.
            beliefs (dict): Beliefs of the agent.
            rules (dict): Rules of the agent.
            plans (dict): Plans of the agent.
            current_step (str): Current step of the agent.
            P (dict): Personality of the agent containing:
                - tr (dict): personality traits
                - rl: rationality level
                - cs (list): set of coping strategies
            Cc: Concerns of the agent
            C (dict): current circumstance represented by a tuple
            composed of:
                - I: set of intentions
                - E: set of events
                - A: set of actions
            T (dict): is the temporary information of the current
            rational cycle consisting of a dictionary containing:
                - "p": Applicable plan.
                - "Ap": Applicable plans.
                - "i": Intention.
                - "R": Relevant plans.
                - "e": Event.
            Mem (dict): Affective memory
            Ta: Temporal information of the affective cycle. Contains:
                - Ub:
                  - Ba: set of beliefs that are going to be added to the belief base
                  - Br: set of beliefs that are going to be removed from the belief base
                  - st: identifier of the step st of the cycle in which the beliefs are
                    going to be added or removed
                - Av: set of appraisal variables
                - Cs: set of coping strategies to be executed
                - Ae: set of emotions that can be elicited by the appraisal process
                - Ee: set of empathic emotions that can be triggered by the empathic
                  appraisal process
                - Fe: the final emotion (or emotions) resulting from the emotion selection
                  process

        """
        super(AffectiveAgent, self).__init__(env, name, beliefs, rules, plans)

        self.current_step = ""

        self.personality = pygenia.personality.personality.Personality()

        # Concerns definition
        self.Cc = collections.defaultdict(lambda: []) if concerns is None else concerns

        # Circunstance definition
        self.C = {"I": collections.deque(), "E": [], "A": []}

        # Temporary information of the current rational cycle definition
        self.T = {"p": None, "Ap": [], "i": None, "R": [], "e": None}

        # Affective memory definition (⟨event 𝜀, affective value av⟩)
        self.Mem = []

        # Temporal information of the affective cycle definition
        self.Ta = TemporalAffectiveInformation()

        # This is an example of the use of affective categories:
        self.affective_categories = {
            "neutral": [
                [-0.3, 0.3],
                [-0.3, 0.3],
                [-1, 1],
            ],
            "happy": [[0, 1], [0, 1], [-1, 1]],
            "sad": [[-1, 0], [-1, 0], [-1, 1]],
        }

        self.event_queue = []

        # self.initAffectiveThreshold()

        self.fulfilledExpectations = []
        self.notFulfilledExpectations = []

        self.AfE = []

    def add_concern(self, concern):
        """
        This method is used to add a concern to the agent.

        Args:
            concern (Concern): Concern to be added.
        """
        self.Cc[(concern.head.functor, len(concern.head.args))].append(concern)

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
        term = agentspeak.evaluate(term, intention.scope)

        if not isinstance(term, agentspeak.Literal):
            raise AslError("expected concern literal, got: '%s'" % term)

        query = TermQuery(term)

        try:
            next(query.execute_concern(self, intention, concern))
            concern_value = " ".join(
                asl_str(agentspeak.freeze(t, intention.scope, {})) for t in term.args
            )
            return concern_value
        except StopIteration:
            return False

    def call(
        self,
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
            self.event_queue.append((term, trigger))
            # self.appraisal((term, trigger),0)
            if trigger == agentspeak.Trigger.addition:
                self.add_belief(term, calling_intention.scope)
            else:
                found = self.remove_belief(term, calling_intention)
                if not found:
                    return True

        # Freeze with caller scope.
        frozen = agentspeak.freeze(term, calling_intention.scope, {})

        if not isinstance(frozen, agentspeak.Literal):
            raise AslError("expected literal")

        # Wake up waiting intentions.
        for intention_stack in self.C["I"]:
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
            for intention_stack in self.C["I"]:
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
            self.add_plan(plan)
            return True

        # If the goal is an askHow and the trigger is an addition, then the agent will find the plan in his list of plans and send it to the agent that asked
        if (
            goal_type == agentspeak.GoalType.askHow
            and trigger == agentspeak.Trigger.addition
        ):
            self.T["e"] = agentspeak.runtime.Event(trigger, goal_type, term.args[2])
            return self._ask_how(term)

        # If the goal is an unTellHow and the trigger is a removal, then the agent will delete the goal from his list of plans
        if (
            goal_type == agentspeak.GoalType.tellHow
            and trigger == agentspeak.Trigger.removal
        ):

            label = term.args[2]

            delete_plan = []
            plans = self.plans.values()
            for plan in plans:
                for differents in plan:
                    if ("@" + str(differents.annotation[0].functor)).startswith(label):
                        delete_plan.append(differents)
            for differents in delete_plan:
                plan.remove(differents)
            return True

        self.C["E"] = (
            [agentspeak.runtime.Event(trigger, goal_type, term)]
            if "E" not in self.C
            else self.C["E"] + [agentspeak.runtime.Event(trigger, goal_type, term)]
        )
        self.current_step = "SelEv"
        self.applySemanticRuleDeliberate(delayed, calling_intention)

        # if goal_type == agentspeak.GoalType.achievement and trigger == agentspeak.Trigger.addition:
        #    raise AslError("no applicable plan for %s%s%s/%d" % (
        #        trigger.value, goal_type.value, frozen.functor, len(frozen.args)))
        # elif goal_type == agentspeak.GoalType.test:
        #    return self.test_belief(term, calling_intention)
        return True

    def applySelEv(self) -> bool:
        """
        This method is used to select the event that will be executed in the next step

        Returns:
            bool: True if the event was selected
        """

        # self.term = self.ast_goal.atom.accept(agentspeak.runtime.BuildTermVisitor({}))
        if "E" in self.C and len(self.C["E"]) > 0:
            # Select one event from the list of events and remove it from the list without using pop
            self.T["e"] = self.C["E"][0]
            self.C["E"] = self.C["E"][1:]
            self.frozen = agentspeak.freeze(
                self.T["e"].head, agentspeak.runtime.Intention().scope, {}
            )
            self.T["i"] = agentspeak.runtime.Intention()
            self.current_step = "RelPl"
        else:
            self.current_step = "SelEv"
            return False

        return True

    def applyRelPl(self) -> bool:
        """
        This method is used to find the plans that are related to the current goal.
        We say that a plan is related to a goal if both have the same functor

        Returns:
            bool: True if the plans were found, False otherwise

        - If the plans were found, the dictionary T["R"] will be filled with the plans found and the current step will be changed to "AppPl"
        - If not plans were found, the current step will be changed to "SelEv" to select a new event
        """

        RelPlan = collections.defaultdict(lambda: [])
        plans = self.plans.values()
        for plan in plans:
            for differents in plan:
                if self.T["e"].head.functor in differents.head.functor:
                    RelPlan[
                        (
                            differents.trigger,
                            differents.goal_type,
                            differents.head.functor,
                            len(differents.head.args),
                        )
                    ].append(differents)

        if not RelPlan:
            self.current_step = "SelEv"
            return False
        self.T["R"] = RelPlan
        self.current_step = "AppPl"
        return True

    def check_affect(self, plan):
        # Return True if the plan has no annotation
        if plan.annotation is None:
            return True
        else:
            # Returns True if the plan has required affect states and the agent's current affect state match any of them
            for a in plan.annotation.annotations:
                if a.functor == "affect__":
                    for t in a.terms:
                        if str(t) in self.AfE:
                            return True

            # Returns False if the agent's current affect does not match any of the required affect states
            return False

    def applyAppPl(self) -> bool:
        """
        This method is used to find the plans that are applicable to the current goal.
        We say that a plan is applicable to a goal if both have the same functor,
        the same number of arguments and the context are satisfied

        Returns:
            bool: True if the plans were found, False otherwise

        - The dictionary T["Ap"] will be filled with:
            + The plans that do not require a specific affective state
            + The plans whose required affective state matches that of the agent
        - The current step will be changed to "SelAppl"
        - If not applicable plans were found, return False
        """
        plans_list = self.T["R"][
            (
                self.T["e"].trigger,
                self.T["e"].goal_type,
                self.frozen.functor,
                len(self.frozen.args),
            )
        ]

        self.T["Ap"] = [plan for plan in plans_list if self.check_affect(plan)]

        self.current_step = "SelAppl"

        return self.T["Ap"] != []

    def applySelAppl(self) -> bool:
        """
        This method is used to select the plan that is applicable to the current goal.
        We say that a plan is applicable to a goal if both have the same functor,
        the same number of arguments and the context are satisfied

        We select the first plan that is applicable to the goal in the dict of
        applicable plans

        Returns:
            bool: True if the plan was found, False otherwise

        - If the plan was found, the dictionary T["p"] will be filled with the plan found and the current step will be changed to "AddIM"
        - If not plan was found, return False
        """
        for plan in self.T["Ap"]:
            for _ in agentspeak.unify_annotated(
                plan.head, self.frozen, self.T["i"].scope, self.T["i"].stack
            ):
                for _ in plan.context.execute(self, self.T["i"]):
                    self.T["p"] = plan
                    self.current_step = "AddIM"
                    return True
        return False

    def applyAddIM(self, delayed, calling_intention) -> bool:
        """
        This method is used to add the intention to the intention stack of the agent

        Returns:
            bool: True if the intention is added to the intention stack

        - When  the intention is added to the intention stack, the current step will be changed to "SelEv"
        """
        self.T["i"].head_term = self.frozen
        self.T["i"].instr = self.T["p"].body
        self.T["i"].calling_term = self.T["e"].head

        if not delayed and self.C["I"]:
            for intention_stack in self.C["I"]:
                if intention_stack[-1] == calling_intention:
                    intention_stack.append(self.T["i"])
                    return False
        new_intention_stack = collections.deque()
        new_intention_stack.append(self.T["i"])

        # Add the event and the intention to the Circumstance
        self.C["I"].append(new_intention_stack)

        self.current_step = "SelInt"
        return True

    def applySemanticRuleDeliberate(
        self, delayed=False, calling_intention=agentspeak.runtime.Intention
    ):
        """
        This method is used to apply the first part of the reasoning cycle.
        This part consists of the following steps:
        - Select an event
        - Find the plans that are related to the event
        - Find the plans that are applicable to the event
        - Select the plan that is applicable to the event
        - Add the intention to the intention stack of the agent
        """
        options = {
            "SelEv": self.applySelEv,
            "RelPl": self.applyRelPl,
            "AppPl": self.applyAppPl,
            "SelAppl": self.applySelAppl,
            "AddIM": self.applyAddIM,
        }

        flag = True
        while flag == True and self.current_step in options:
            if self.current_step == "AddIM":
                flag = options[self.current_step](delayed, calling_intention)
            else:
                flag = options[self.current_step]()

        return True

    def affectiveTransitionSystem(self):
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

    def appraisal(self, event, concern_value):
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
            if len(self.Cc):
                desirability = self.desirability(event)
                self.Ta.get_appraisal_variables()["desirability"] = desirability

            # Calculating likelihood.
            likelihood = self.likelihood(event)
            self.Ta.get_appraisal_variables()["likelihood"] = likelihood

            # Calculating causal attribution
            causal_attribution = self.causalAttribution(event)
            self.Ta.get_appraisal_variables()["causal_attribution"] = causal_attribution

            # Calculating controllability:
            if len(self.Cc):
                controllability = self.controllability(
                    event, concern_value, desirability
                )
                self.Ta.get_appraisal_variables()["controllability"] = controllability
                pass
            result = True
        else:
            self.Ta.get_appraisal_variables()["desirability"] = None
            self.Ta.get_appraisal_variables()["expectedness"] = None
            self.Ta.get_appraisal_variables()["likelihood"] = None
            self.Ta.get_appraisal_variables()["causal_attribution"] = None
            self.Ta.get_appraisal_variables()["controllability"] = None
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

    def desirability(self, event):
        """
        This method is used to calculate the desirability of the event.

        Args:
            event (tuple): Event to be appraised.

        Returns:
            float: Desirability of the event.
        """
        concernVal = None
        # This function return the first concern of the agent
        concern = self.Cc[("concern__", 1)][0]

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

    def applyAppraisal(self) -> bool:
        """
        This method is used to apply the appraisal process.
        """
        ped = PairEventDesirability(None)
        if True:  # while self.lock instead of True for the real implementation
            if self.event_queue:
                ped.event = self.event_queue.pop()

        if ped.event == None:
            self.appraisal(None, 0.0)
            self.currentEvent = None
            self.eventProcessedInCycle = False
        else:
            self.appraisal(ped.event, random.random())
            self.currentEvent = ped.event
            self.eventProcessedInCycle = True

        if self.cleanAffectivelyRelevantEvents():
            self.Mem = []

        # The next step is Update Aff State
        self.current_step_ast = "UpAs"
        return True

    def applyCope(self):
        """
        This method is used to apply the coping process.
        """

        SelectingCs = True
        while SelectingCs and self.C["CS"]:
            SelectingCs = self.cope()
        # self.current_step_ast = "Appr"
        return False

    def cope(self):
        """
        This method is used to apply the coping process.

        Returns:
            bool: True if the coping strategy was applied, False otherwise.
        """

        if self.C["CS"]:
            cs = self.C["CS"].pop(0)
            self["CS"].append(cs)
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
        self.C["CS"] = []
        # self.selectCs()
        self.current_step_ast = "Cope"
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

    def applyUpdateAffState(self):
        """
        This method is used to update the affective state.
        """
        if self.eventProcessedInCycle:
            self.UpdateAS()
        if self.isAffectRelevantEvent(self.currentEvent):
            self.Mem.append(self.currentEvent)
        self.current_step_ast = "SelCs"
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

        for ex in self.Ta.get_mood().affRevEventThreshold:
            result = result and ex.evaluate(
                self.Ta.get_mood().getP(),
                self.Ta.get_mood().getA(),
                self.Ta.get_mood().getD(),
            )
        return result

    def UpdateAS(self):
        """
        This method is used to update the affective state.
        """
        self.DISPLACEMENT = 0.5
        if isinstance(self.Ta.get_mood(), PAD):
            pad = PAD()
            calculated_as = self.deriveASFromAppraisalVariables()

            if calculated_as != None:
                # PAD current_as = (PAD) getAS();
                current_as = self.Ta.get_mood()

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

                self.Ta.set_mood(pad)
                AClabel = self.getACLabel()
                self.AfE = AClabel
        pass

    def getACLabel(self):
        """
        This method is used to get the affective category label.

        Returns:
            list: Affective category label.
        """

        result = []
        matches = True
        r = None
        for acl in self.affective_categories.keys():
            matches = True
            if self.affective_categories[acl] != None:
                if len(self.affective_categories[acl]) == len(
                    self.Ta.get_mood().affectiveLabels
                ):
                    for i in range(len(self.Ta.get_mood().affectiveLabels)):
                        r = self.affective_categories[acl][i]
                        matches = (
                            matches
                            and self.Ta.get_mood().components[i] >= r[0]
                            and self.Ta.get_mood().components[i] <= r[1]
                        )
                else:
                    try:
                        raise Exception(
                            "The number of components for the affective category "
                            + acl
                            + " must be the same as the number of the components for the affective state"
                        )
                    except Exception as e:
                        print(e)
            if matches:
                result.append(acl)
        return result

    def deriveASFromAppraisalVariables(self):
        """
        This method is used to derive the affective state from the appraisal variables.

        Returns:
            PAD: Affective state.
        """
        em = []

        if (
            self.Ta.get_appraisal_variables()["expectedness"] != None
            and self.Ta.get_appraisal_variables()["expectedness"] < 0
        ):
            em.append("surprise")
        if (
            self.Ta.get_appraisal_variables()["desirability"] != None
            and self.Ta.get_appraisal_variables()["likelihood"] != None
        ):
            if self.Ta.get_appraisal_variables()["desirability"] > 0.5:
                if self.Ta.get_appraisal_variables()["likelihood"] < 1:
                    em.append("hope")
                elif self.Ta.get_appraisal_variables()["likelihood"] == 1:
                    em.append("joy")
            else:
                if self.Ta.get_appraisal_variables()["likelihood"] < 1:
                    em.append("fear")
                elif self.Ta.get_appraisal_variables()["likelihood"] == 1:
                    em.append("sadness")
                if (
                    self.Ta.get_appraisal_variables()["causal_attribution"] != None
                    and self.Ta.get_appraisal_variables()["controllability"] != None
                    and self.Ta.get_appraisal_variables()["causal_attribution"]
                    == "other"
                    and self.Ta.get_appraisal_variables()["controllability"] > 0.7
                ):
                    em.append("anger")
        result = PAD()
        result.setP(0.0)
        result.setA(0.0)
        result.setD(0.0)

        for e in em:
            if e == "anger":
                result.setP(result.getP() - 0.51)
                result.setA(result.getA() + 0.59)
                result.setD(result.getD() + 0.25)
            elif e == "fear":
                result.setP(result.getP() - 0.64)
                result.setA(result.getA() + 0.60)
                result.setD(result.getD() - 0.43)
            elif e == "hope":
                result.setP(result.getP() + 0.2)
                result.setA(result.getA() + 0.2)
                result.setD(result.getD() - 0.1)
            elif e == "joy":
                result.setP(result.getP() + 0.76)
                result.setA(result.getA() + 0.48)
                result.setD(result.getD() + 0.35)
            elif e == "sadness":
                result.setP(result.getP() - 0.63)
                result.setA(result.getA() - 0.27)
                result.setD(result.getD() - 0.33)
            elif e == "surprise":
                result.setP(result.getP() + 0.4)
                result.setA(result.getA() + 0.67)
                result.setD(result.getD() - 0.13)

        # Averaging
        if len(em) > 0:
            result.setP(result.getP() / len(em))
            result.setA(result.getA() / len(em))
            result.setD(result.getD() / len(em))
        else:
            result = None
        return result

    def cleanAffectivelyRelevantEvents(self) -> bool:
        return True

    def step(self) -> bool:
        """
        This method is used to apply the second part of the reasoning cycle.
        This method consist in selecting the intention to execute and executing it.
        This part consists of the following steps:
        - Select the intention to execute
        - Apply the clear intention
        - Apply the execution intention

        Raises:
            log.error: If the agent has no intentions
            log.exception: If the agent raises a python exception

        Returns:
            bool: True if the agent executed or cleaned an intention, False otherwise
        """
        options = {
            "SelInt": self.applySelInt,
            "CtlInt": self.applyCtlInt,
            "ExecInt": self.applyExecInt,
        }

        if self.current_step == "SelInt":
            if not options[self.current_step]():
                return False

        if self.current_step in options:
            flag = options[self.current_step]()
            return flag
        else:
            return True

    def applySelInt(self) -> bool:
        """
        This method is used to select the intention to execute

        Raises:
            RuntimeError:  If the agent has no intentions

        Returns:
            bool: True if the agent has intentions, False otherwise

        - If the intention not have instructions, the current step will be changed to "CtlInt" to clear the intention
        - If the intention have instructions, the current step will be changed to "ExecInt" to execute the intention

        """
        while self.C["I"] and not self.C["I"][0]:
            self.C["I"].popleft()

        for intention_stack in self.C["I"]:
            if not intention_stack:
                continue
            intention = intention_stack[-1]
            if intention.waiter is not None:
                if intention.waiter.poll(self.env):
                    intention.waiter = None
                else:
                    continue
            break
        else:
            return False

        if not intention_stack:
            return False

        instr = intention.instr
        self.intention_stack = intention_stack
        self.intention_selected = intention

        if not instr:
            self.current_step = "CtlInt"
        else:
            self.current_step = "ExecInt"

        return True

    def applyExecInt(self) -> bool:
        """
        This method is used to execute the instruction

        Raises:
            AslError: If the plan fails

        Returns:
            bool: True if the instruction was executed
        """
        try:
            if self.intention_selected.instr.f(self, self.intention_selected):
                # We set the intention.instr to the instr.success
                self.intention_selected.instr = self.intention_selected.instr.success

            else:
                # We set the intention.instr to the instr.failure
                self.intention_selected.instr = self.intention_selected.instr.failure
                if not self.T["i"].instr:
                    raise AslError("plan failure")

        except AslError as err:
            log = agentspeak.Log(LOGGER)
            raise log.error(
                "%s",
                err,
                loc=self.T["i"].instr.loc,
                extra_locs=self.T["i"].instr.extra_locs,
            )
        except Exception as err:
            log = agentspeak.Log(LOGGER)
            raise log.exception(
                "agent %r raised python exception: %r",
                self.name,
                err,
                loc=self.T["i"].instr.loc,
                extra_locs=self.T["i"].instr.extra_locs,
            )
        return True

    def applyCtlInt(self) -> True:
        """
        This method is used to control the intention

        Returns:
            bool: True if the intention was cleared
        """
        self.intention_stack.pop()
        if not self.intention_stack:
            self.C["I"].remove(self.intention_stack)
        elif self.intention_selected.calling_term:
            frozen = self.intention_selected.head_term.freeze(
                self.intention_selected.scope, {}
            )

            calling_intention = self.intention_stack[-1]
            if not agentspeak.unify(
                self.intention_selected.calling_term,
                frozen,
                calling_intention.scope,
                calling_intention.stack,
            ):
                raise RuntimeError("back unification failed")
        return True

    def waiters(self) -> Iterator[agentspeak.runtime.Waiter]:
        """
        This method is used to get the waiters of the intentions

        Returns:
            Iterator[agentspeak.runtime.Waiter]: The waiters of the intentions
        """
        return (
            intention[-1].waiter
            for intention in self.C["I"]
            if intention and intention[-1].waiter
        )

    def run(self, affective_turns=1, rational_turns=1) -> None:
        """
        This method is used to run a cycle of the agent
        """

        async def main():

            def release_sem(sem, turns, flag):
                if flag:
                    for i in range(turns):
                        sem.release()

            # Affective cycle
            async def affective():
                while not end_event.is_set():
                    await sem_affective.acquire()
                    self.current_step_ast = "Appr"
                    self.affectiveTransitionSystem()
                    release_sem(sem_rational, rational_turns, sem_affective.locked())

            # Rational cycle
            async def rational():
                while not end_event.is_set():
                    await sem_rational.acquire()
                    if "E" in self.C:
                        for i in range(len(self.C["E"])):
                            self.current_step = "SelEv"
                            self.applySemanticRuleDeliberate()

                    self.current_step = "SelInt"
                    if not self.step():
                        end_event.set()

                    release_sem(sem_affective, affective_turns, sem_rational.locked())

            # Create the semaphores that will be used to synchronize the two functions
            sem_affective = asyncio.Semaphore(affective_turns)
            sem_rational = asyncio.Semaphore(0)

            # Create an event to finish the processes
            end_event = asyncio.Event()

            # Create the two tasks that will run the functions
            task1 = asyncio.create_task(affective())
            task2 = asyncio.create_task(rational())

            # Wait for both tasks to complete
            await asyncio.gather(task1, task2)

        asyncio.run(main())

        return False


class Concern:
    """
    This class is used to represent the concern of the agent
    """

    def __init__(self, head, query):
        self.head = head
        self.query = query

    def __str__(self):
        return "%s :- %s" % (self.head, self.query)


class PairEventDesirability:
    def __init__(self, event):
        self.event = event
        self.av = {}
