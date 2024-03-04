#!/usr/bin/env python

import agentspeak.stdlib
import pygenia.affective_agent
import pygenia.personality.ocean_personality
import pygenia.environment
import pygenia.emotion_models.pa
import pygenia.cognitive_engine.default_engine

import os


env = pygenia.environment.Environment()
agent_cls = pygenia.affective_agent.AffectiveAgent
personality_cls = pygenia.personality.ocean_personality.OceanPersonality
affst_cls = pygenia.emotion_models.pa.PAModel
em_engine_cls = pygenia.cognitive_engine.default_engine.DefaultEngine


with open(os.path.join(os.path.dirname(__file__), "agent1.asl")) as source:
    agents = env.build_agents(
        source,
        1,
        agentspeak.stdlib.actions,
        agent_cls=agent_cls,
        em_engine_cls=em_engine_cls,
        personality_cls=personality_cls,
        affst_cls=affst_cls,
    )

if __name__ == "__main__":
    env.run()
