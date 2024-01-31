#!/usr/bin/env python

import agentspeak.stdlib
import pygenia.affective_agent

import os


env = pygenia.affective_agent.Environment()
agent = pygenia.affective_agent.AffectiveAgent

with open(os.path.join(os.path.dirname(__file__), "agent1.asl")) as source:
    agents = env.build_agents(source, 1, agentspeak.stdlib.actions, agent)

if __name__ == "__main__":
    env.run()
