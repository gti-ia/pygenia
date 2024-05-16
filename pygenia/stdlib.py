from __future__ import print_function, division

import agentspeak
import agentspeak.optimizer
import agentspeak.runtime
from agentspeak.stdlib import actions
from scipy.optimize import linprog
import math


@actions.add(".print_afflb")
@agentspeak.optimizer.no_scope_effects
def _print_afflb(agent, term, intention):
    print(agent.AfE)

    yield


@actions.add(".get_affst_pa", 2)
@actions.add(".get_affst_pad", 3)
@agentspeak.optimizer.function_like
def _get_affst(agent, term, intention):
    if agentspeak.unify(
        term.args[0],
        agent.affective_info.get_mood().get_pleasure(),
        intention.scope,
        intention.stack,
    ):
        if agentspeak.unify(
            term.args[1],
            agent.affective_info.get_mood().get_arousal(),
            intention.scope,
            intention.stack,
        ):
            if len(term.args) > 2:
                if agentspeak.unify(
                    term.args[2],
                    agent.affective_info.get_mood().get_dominance(),
                    intention.scope,
                    intention.stack,
                ):
                    yield
            else:
                yield


@actions.add(".get_concern", 1)
@agentspeak.optimizer.function_like
def _get_concern_value(agent, term, intention):
    if agentspeak.unify(
        term.args[0],
        agent.emotional_engine.get_concern_value(),
        intention.scope,
        intention.stack,
    ):
        yield


@actions.add(".get_empathic_concern", 1)
@agentspeak.optimizer.function_like
def _get_empathic_concern_value(agent, term, intention):
    if agentspeak.unify(
        term.args[0],
        agent.emotional_engine.get_empathic_concern_value(),
        intention.scope,
        intention.stack,
    ):
        yield


@actions.add(".estimate_offer_ug", 3)
@agentspeak.optimizer.function_like
def _estimate_offer(agent, term, intention):
    threshold = float(agentspeak.evaluate(term.args[0], intention.scope))
    previous_offer = float(agentspeak.evaluate(term.args[1], intention.scope))
    w_link = 0.5
    w_emph = agent.personality.get_empathic_level()
    new_offer = 0.1
    if len(agent.emotional_engine.get_empathic_emotions()) > 0:
        # new_offer = (
        #    1
        #    / (
        #        float(agent.emotional_engine.get_empathic_emotions()[0].get_pleasure())
        #        + 1
        #    )
        #    / 2
        # ) * w_emph + float(agent.others["responder"]["affective_link"]) * w_link
        others_emotion = agent.emotional_engine.get_empathic_emotions()[
            0
        ].get_pleasure()
        affective_link = agent.others["responder"]["affective_link"]
        mood = agent.emotional_engine.affective_info.get_mood().mood.get_pleasure()
        empathic_level = agent.personality.get_empathic_level()
        new_offer = float(
            1
            / (
                5
                - (affective_link + (1 + mood)) * empathic_level
                + math.exp(5 * (others_emotion + -affective_link))
            )
        )
        print(
            "---___",
            new_offer,
            others_emotion,
            agent.emotional_engine.affective_info.get_mood().mood,
            affective_link,
            empathic_level,
        )
    if agentspeak.unify(
        term.args[2],
        new_offer,
        intention.scope,
        intention.stack,
    ):
        yield
