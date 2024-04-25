from __future__ import print_function

import asyncio
import collections
from typing import Iterator

import agentspeak
import agentspeak.runtime
import agentspeak.stdlib
import agentspeak.util
from agentspeak import AslError


import pygenia.lexer
import pygenia.parser
import pygenia.stdlib
import pygenia.personality.personality
from pygenia.utils import (
    TrueQuery,
    Instruction,
    BuildInstructionsVisitor,
    BuildQueryVisitor,
)
from pygenia.cognitive_engine.default_engine import DefaultEngine
from pygenia.cognitive_engine.circumstance import Circumstance
from pygenia.cognitive_engine.rational_processes import RationalCycle

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
        """
        super(AffectiveAgent, self).__init__(env, name, beliefs, rules, plans)

        self.emotional_engine = None  # DefaultEngine(agent=self)

        self.rational_cycle = RationalCycle(agent=self)

        # Circunstance definition
        self.circumstance = Circumstance()

        self.rational_cycle.set_circumstance(self.circumstance)

        self.personality = None

        # Concerns definition
        self.concerns = (
            collections.defaultdict(lambda: []) if concerns is None else concerns
        )

        # Affective memory definition (⟨event 𝜀, affective value av⟩)
        self.Mem = []

        self.event_queue = []

        self.personality_emotion_matrix = {}

    def set_personality_emotion_matrix(self, personality_emotion_matrix):
        self.personality_emotion_matrix = personality_emotion_matrix

    def set_emotional_engine(self, em_engine_cls, affst_cls):
        self.emotional_engine = em_engine_cls(agent=self, affst_cls=affst_cls)
        self.emotional_engine.set_circumstance(self.circumstance)
        # CHECK TODO set the concerns of default engine to this concerns
        self.emotional_engine.set_concerns(self.concerns)
        # TODO set the event_queue of default engine to this queue
        self.emotional_engine.set_event_queue(self.event_queue)

    def set_personality_cls(self, personality_cls):
        self.personality = personality_cls()

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
        for intention_stack in self.circumstance.get_intentions():
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
            for intention_stack in self.circunstance.get_intentions():
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

        current_event = agentspeak.runtime.Event(trigger, goal_type, term)
        self.circumstance.add_event(current_event)
        self.rational_cycle.set_current_step("SelEv")
        # self.current_step = "SelEv"
        # self.applySemanticRuleDeliberate(delayed, calling_intention)
        self.rational_cycle.applySemanticRuleDeliberate(delayed, calling_intention)

        # if goal_type == agentspeak.GoalType.achievement and trigger == agentspeak.Trigger.addition:
        #    raise AslError("no applicable plan for %s%s%s/%d" % (
        #        trigger.value, goal_type.value, frozen.functor, len(frozen.args)))
        # elif goal_type == agentspeak.GoalType.test:
        #    return self.test_belief(term, calling_intention)
        return True

    def add_concern(self, concern):
        """
        This method is used to add a concern to the agent.

        Args:
            concern (Concern): Concern to be added.
        """
        self.concerns[(concern.head.functor, len(concern.head.args))].append(concern)

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
        concern_value = self.emotional_engine.test_concern(
            concern.head, agentspeak.runtime.Intention(), concern
        )
        # We add the belief to the agent's belief base again
        # self.add_belief(event[0], agentspeak.runtime.Intention())

        return concern_value

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
                    self.emotional_engine.current_step_ast = "Appr"
                    self.emotional_engine.affective_transition_system()
                    release_sem(sem_rational, rational_turns, sem_affective.locked())

            # Rational cycle
            async def rational():
                while not end_event.is_set():
                    await sem_rational.acquire()
                    if len(self.circumstance.get_events()) > 0:
                        for i in range(len(self.circumstance.get_events())):
                            self.rational_cycle.set_current_step("SelEv")
                            self.rational_cycle.applySemanticRuleDeliberate()

                    self.rational_cycle.set_current_step("SelInt")

                    if not self.rational_cycle.step():
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
