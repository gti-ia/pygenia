#!/usr/bin/env python

import agentspeak.stdlib
import agentspeak.runtime
import pygenia.affective_agent
import pygenia.personality.ocean_personality
import pygenia.environment
import pygenia.emotion_models.pa
import pygenia.cognitive_engine.default_engine
import pygenia.cognitive_engine.empathic_engine
import pygenia.emotion_models.pad
import pygenia.empathic_environment
import pygenia.empathic_agent
import os

# env = agentspeak.runtime.Environment()
# env = pygenia.environment.Environment()
env = pygenia.empathic_environment.EmpathicEnvironment()
responder_agent_cls = pygenia.affective_agent.AffectiveAgent
proposer_agent_cls = pygenia.empathic_agent.EmpathicAgent
personality_cls = pygenia.personality.ocean_personality.OceanPersonality
affst_cls = pygenia.emotion_models.pa.PAModel
responder_em_engine_cls = pygenia.cognitive_engine.default_engine.DefaultEngine
proposer_em_engine_cls = pygenia.cognitive_engine.empathic_engine.EmpathicEngine

with open(os.path.join(os.path.dirname(__file__), "proposer.asl")) as source:
    agents = env.build_agents(
        source,
        1,
        agentspeak.stdlib.actions,
        # agent_cls=responder_agent_cls,
        # em_engine_cls=responder_em_engine_cls,
        # personality_cls=personality_cls,
        # affst_cls=affst_cls,
        agent_cls=proposer_agent_cls,
        em_engine_cls=proposer_em_engine_cls,
        personality_cls=personality_cls,
        affst_cls=affst_cls,
        affst_parameters=["english"],
    )

with open(os.path.join(os.path.dirname(__file__), "responder.asl")) as source:
    agents = env.build_agents(
        source,
        1,
        agentspeak.stdlib.actions,
        # agent_cls=responder_agent_cls,
        # em_engine_cls=responder_em_engine_cls,
        # personality_cls=personality_cls,
        # affst_cls=affst_cls,
        agent_cls=responder_agent_cls,
        em_engine_cls=responder_em_engine_cls,
        personality_cls=personality_cls,
        affst_cls=affst_cls,
    )

if __name__ == "__main__":
    env.run()
