from __future__ import print_function, division

import agentspeak
import agentspeak.optimizer
import agentspeak.runtime
from agentspeak.stdlib import actions

@actions.add(".print_afflb")
@agentspeak.optimizer.no_scope_effects
def _print_afflb(agent, term, intention):
    print(agent.AfE)

    yield

@actions.add(".get_affst", 2)
@actions.add(".get_affst", 3)
@agentspeak.optimizer.function_like
def _my_name(agent, term, intention):
    if agentspeak.unify(term.args[0], agent.Ta['mood'].getP(), intention.scope, intention.stack):
        if agentspeak.unify(term.args[1], agent.Ta['mood'].getA(), intention.scope, intention.stack):
            if len(term.args) > 2:
                if agentspeak.unify(term.args[2], agent.Ta['mood'].getD(), intention.scope, intention.stack):  
                    yield
            else:
                yield