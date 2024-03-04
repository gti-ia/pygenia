from __future__ import print_function

import collections
import agentspeak
from typing import Iterator
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util
from agentspeak import AslError
from agentspeak.runtime import Event

from pygenia.cognitive_engine.circumstance import Circumstance

LOGGER = agentspeak.get_logger(__name__)
C = {}


class RationalCycle:
    def __init__(self, agent):
        self.current_step = ""
        self._applicable_plan = None
        self._applicable_plans = []
        self._intention = None
        self._relevant_plans = []
        self._event: Event = None
        self.circumstance: Circumstance = None
        self.affective_categories = None  # TODO remove this variable
        self.agent = agent

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

    def applySelEv(self) -> bool:
        """
        This method is used to select the event that will be executed in the next step

        Returns:
            bool: True if the event was selected
        """
        # self.term = self.ast_goal.atom.accept(agentspeak.runtime.BuildTermVisitor({}))
        # if "E" in self.C and len(self.C["E"]) > 0:
        if self.circumstance.get_num_events() > 0:
            # Select one event from the list of events and remove it from the list without using pop
            event = self.circumstance.get_event_at_index(0)
            self.set_event(event)
            # self.C["E"] = self.C["E"][1:]
            self.circumstance.remove_event_at_index(0)
            self.frozen = agentspeak.freeze(
                event.head, agentspeak.runtime.Intention().scope, {}
            )
            self.set_intention(agentspeak.runtime.Intention())
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
        plans = self.agent.plans.values()
        RelPlan = collections.defaultdict(lambda: [])
        # TODO plans was self.plans.values()
        for plan in plans:
            for differents in plan:
                if self.get_event().head.functor in differents.head.functor:
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
        self.set_relevant_plans(RelPlan)
        self.current_step = "AppPl"
        return True

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
        plans_list = self.get_relevant_plans()[
            (
                self.get_event().trigger,
                self.get_event().goal_type,
                self.frozen.functor,  # TODO frozen_functor was self.frozen.functor,
                len(self.frozen.args),  # TODO frozen_args was (self.frozen.args,
            )
        ]

        applicable_plans = [plan for plan in plans_list if self.check_affect(plan)]
        self.set_applicable_plans(applicable_plans)
        # TODO applicable plans must be subdivided in two rational and affective plans to create the two rankings
        self.current_step = "SelAppl"

        return self.get_applicable_plans() != []

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

        for plan in self.get_applicable_plans():
            for _ in agentspeak.unify_annotated(
                plan.head,
                self.frozen,
                self.get_intention().scope,
                self.get_intention().stack,
            ):
                for _ in plan.context.execute(self, self.get_intention()):
                    self.set_applicable_plan(plan)
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
        self._intention.head_term = self.frozen
        # TODO frozen was self.frozen from agent
        self._intention.instr = self._applicable_plan.body
        self._intention.calling_term = self._applicable_plan.head

        if not delayed and self.circumstance.get_intentions():
            for intention_stack in self.circumstance.get_intentions():
                if intention_stack[-1] == calling_intention:
                    intention_stack.append(self._intention)
                    return False

        new_intention_stack = collections.deque()
        new_intention_stack.append(self._intention)
        # Add the event and the intention to the Circumstance
        self.circumstance.add_intention(new_intention_stack)
        # self.C["I"].append(new_intention_stack)
        self.current_step = "SelInt"

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
        while (
            self.circumstance.get_intentions()
            and not self.circumstance.get_intentions()[0]
        ):
            self.circumstance.set_intentions(
                self.circumstance.get_intentions().popleft()
            )
        # while self.C["I"] and not self.C["I"][0]:
        # self.C["I"].popleft()
        for intention_stack in self.circumstance.get_intentions():
            if not intention_stack:
                continue
            intention = intention_stack[-1]
            if intention.waiter is not None:
                if intention.waiter.poll(self.agent.env):
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
            if self.intention_selected.instr.f(self.agent, self.intention_selected):
                # We set the intention.instr to the instr.success
                self.intention_selected.instr = self.intention_selected.instr.success
            else:
                # We set the intention.instr to the instr.failure
                self.intention_selected.instr = self.intention_selected.instr.failure

                if not self._intention.instr:
                    raise AslError("plan failure")

        except AslError as err:
            log = agentspeak.Log(LOGGER)
            raise log.error(
                "%s",
                err,
                loc=self._intention.instr.loc,
                extra_locs=self._intention.instr.extra_locs,
            )
        except Exception as err:
            log = agentspeak.Log(LOGGER)
            raise log.exception(
                "agent %r raised python exception: %r",
                self.agent.name,
                err,
                loc=self._intention.instr.loc,
                extra_locs=self._intention.instr.extra_locs,
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
            self.circumstance.delete_intention(self.intention_stack)
            # self.C["I"].remove(self.intention_stack)
        elif self.intention_selected.calling_term:
            frozen = self.intention_selected.head_term.freeze(
                self.intention_selected.scope, {}
            )

            calling_intention = self.intention_stack[-1]
            if not agentspeak.unify(
                self.intention_selected.calling_term,
                frozen,
                self.intention_selected.scope,
                # TODO this was calling_intention.scope it must be necesari to compare it
                self.intention_selected.stack,
                # TODO this was calling_intention.stack it must be necesari to compare it
            ):
                raise RuntimeError("back unification failed")
                pass
        return True

    def waiters(
        self, circumstance: Circumstance
    ) -> Iterator[agentspeak.runtime.Waiter]:
        """
        This method is used to get the waiters of the intentions

        Returns:
            Iterator[agentspeak.runtime.Waiter]: The waiters of the intentions
        """
        return (
            intention[-1].waiter
            for intention in circumstance.get_intentions()
            if intention and intention[-1].waiter
        )

    # TODO move this method to the default emotion engine once the affective state is set
    def check_affect(self, plan):
        # Return True if the plan has no annotation
        if plan.annotation is None:
            return True
        else:
            # Returns True if the plan has required affect states and the agent's current affect state match any of them
            for annotation in plan.annotation.annotations:
                if annotation.functor == "affect__":
                    for term in annotation.terms:
                        if (
                            str(term)
                            in self.agent.emotional_engine.affective_info.get_mood().get_affective_labels()
                        ):  # TODO affective_state was self.AfE
                            return True

            # Returns False if the agent's current affect does not match any of the required affect states
            return False
        return True

    def insert_applicable_plan(self, item):
        self._applicable_plan = item

    def insert_applicable_plans(self, item):
        self._applicable_plans.append(item)

    def delete_applicable_plans(self, item):
        if item in self._applicable_plans:
            self._applicable_plans.remove(item)
        else:
            print("Item not found in applicable_plans")

    def search_applicable_plans(self, item):
        return item in self._applicable_plans

    def insert_intention(self, item):
        self._intention = item

    def insert_relevant_plans(self, item):
        self._relevant_plans.append(item)

    def delete_relevant_plans(self, item):
        if item in self._relevant_plans:
            self._relevant_plans.remove(item)
        else:
            print("Item not found in relevant_plans")

    def search_relevant_plans(self, item):
        return item in self._relevant_plans

    def insert_event(self, item):
        self._event = item

    # Getter and setter for applicable_plan
    def get_applicable_plan(self):
        return self._applicable_plan

    def set_applicable_plan(self, value):
        self._applicable_plan = value

    # Getter and setter for applicable_plans
    def get_applicable_plans(self):
        return self._applicable_plans

    def set_applicable_plans(self, values):
        self._applicable_plans = values

    # Getter and setter for intention
    def get_intention(self):
        return self._intention

    def set_intention(self, value):
        self._intention = value

    # Getter and setter for relevant_plans
    def get_relevant_plans(self):
        return self._relevant_plans

    def set_relevant_plans(self, values):
        self._relevant_plans = values

    # Getter and setter for event
    def get_event(self):
        return self._event

    def set_event(self, value: Event):
        self._event = value

    def get_current_step(self):
        return self.current_step

    def set_current_step(self, step):
        self.current_step = step

    def set_circumstance(self, circumstance):
        self.circumstance = circumstance

    def set_affective_categories(self, affective_categories):
        self.affective_categories = affective_categories

    def set_agent(self, agent):
        self.agent = agent
