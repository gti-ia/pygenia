#!/usr/bin/env python

import agentspeak.stdlib
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

env = pygenia.empathic_environment.EmpathicEnvironment()
alice_agent_cls = pygenia.affective_agent.AffectiveAgent
bob_agent_cls = pygenia.empathic_agent.EmpathicAgent
personality_cls = pygenia.personality.ocean_personality.OceanPersonality
affst_cls = pygenia.emotion_models.pa.PAModel
alice_em_engine_cls = pygenia.cognitive_engine.default_engine.DefaultEngine
bob_em_engine_cls = pygenia.cognitive_engine.empathic_engine.EmpathicEngine

with open(os.path.join(os.path.dirname(__file__), "bob.asl")) as source:
    agents = env.build_agents(
        source,
        1,
        agentspeak.stdlib.actions,
        agent_cls=bob_agent_cls,
        em_engine_cls=bob_em_engine_cls,
        personality_cls=personality_cls,
        affst_cls=affst_cls,
    )

with open(os.path.join(os.path.dirname(__file__), "alice.asl")) as source:
    agents = env.build_agents(
        source,
        1,
        agentspeak.stdlib.actions,
        agent_cls=alice_agent_cls,
        em_engine_cls=alice_em_engine_cls,
        personality_cls=personality_cls,
        affst_cls=affst_cls,
    )

if __name__ == "__main__":
    env.run()
