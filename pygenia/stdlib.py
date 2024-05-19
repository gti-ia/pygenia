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


@actions.add(".get_pleasure", 1)
@agentspeak.optimizer.function_like
def _get_pleasure(agent, term, intention):
    mood = agent.emotional_engine.affective_info.get_mood().mood.get_pleasure()
    if agentspeak.unify(
        term.args[0],
        mood,
        intention.scope,
        intention.stack,
    ):
        yield


@actions.add(".get_empathic_pleasure", 1)
@agentspeak.optimizer.function_like
def _get_empathic_pleasure(agent, term, intention):
    try:
        others_emotion = agent.emotional_engine.get_empathic_emotions()[
            0
        ].get_pleasure()
    except:
        others_emotion = 0.0
    if agentspeak.unify(
        term.args[0],
        others_emotion,
        intention.scope,
        intention.stack,
    ):
        yield


@actions.add(".estimate_offer_ug", 4)
@agentspeak.optimizer.function_like
def _estimate_offer(agent, term, intention):
    threshold = float(agentspeak.evaluate(term.args[0], intention.scope))
    previous_offer = float(agentspeak.evaluate(term.args[1], intention.scope))
    response = str(agentspeak.evaluate(term.args[3], intention.scope))
    w_link = 0.5
    w_emph = agent.personality.get_empathic_level()
    new_offer = 0.1
    try:
        others_emotion = agent.emotional_engine.get_empathic_emotions()[
            0
        ].get_pleasure()
    except:
        others_emotion = 0.0
    affective_link = agent.others["responder"]["affective_link"]
    mood = agent.emotional_engine.affective_info.get_mood().mood.get_pleasure()
    empathic_level = agent.personality.get_empathic_level()
    if response == "reject":
        # new_offer = (
        #    1
        #    / (
        #        float(agent.emotional_engine.get_empathic_emotions()[0].get_pleasure())
        #        + 1
        #    )
        #    / 2
        # ) * w_emph + float(agent.others["responder"]["affective_link"]) * w_link
        new_offer = previous_offer + 0.05
    else:
        new_offer = round(
            float(
                1
                / (
                    5
                    - (affective_link + (1 + mood)) * empathic_level
                    + math.exp(5 * (others_emotion + -affective_link))
                )
            )
            * 10,
            2,
        )
    if agentspeak.unify(
        term.args[2],
        new_offer,
        intention.scope,
        intention.stack,
    ):
        yield
