from __future__ import print_function

import agentspeak
import pygenia.affective_agent
from pygenia.affective_agent import AffectiveAgent
import asyncio

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

    def get_other(self, other_id: str):
        return self.others[other_id]

    def update_affective_link(self, agent_id, interaction_value):
        if self.others is not None:
            if agent_id in self.others.keys():
                self.others[agent_id]["affective_link"] += interaction_value
            else:
                self.others.setdefault(agent_id, {"affective_link": interaction_value})

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
                    self.emotional_engine.current_step_ast = "EvClass"
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
