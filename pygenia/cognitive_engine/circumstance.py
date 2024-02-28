import collections
from agentspeak.runtime import Event


class Circumstance:
    """
    A class representing a circumstance, which encapsulates intentions, events, and actions.

    Attributes:
    - _intentions: A deque (double-ended queue) containing intentions.
    - _events: A list containing events.
    - _actions: A list containing actions.
    """

    def __init__(self):
        self._intentions = collections.deque()
        self._events: Event = []
        self._actions = []

    # Getter and setter methods for _intentions
    def get_intentions(self):
        return self._intentions

    def set_intentions(self, intentions):
        self._intentions = intentions

    # Method to add an intention
    def add_intention(self, intention):
        self._intentions.append(intention)

    # Method to search for an intention
    def search_intention(self, intention):
        return intention in self._intentions

    # Method to delete an intention
    def delete_intention(self, intention):
        try:
            self._intentions.remove(intention)
        except ValueError:
            print("Intention not found.")

    # Getter and setter methods for _events
    def get_events(self):
        return self._events

    def set_events(self, events):
        self._events = events

    # Method to add an event
    def add_event(self, event):
        self._events.append(event)

    # Method to search for an event
    def search_event(self, event):
        return event in self._events

    # Method to delete an event
    def delete_event(self, event):
        if event in self._events:
            self._events.remove(event)
        else:
            print("Event not found.")

    # Getter and setter methods for _actions
    def get_actions(self):
        return self._actions

    def set_actions(self, actions):
        self._actions = actions

    # Method to add an action
    def add_action(self, action):
        self._actions.append(action)

    # Method to search for an action
    def search_action(self, action):
        return action in self._actions

    # Method to delete an action
    def delete_action(self, action):
        if action in self._actions:
            self._actions.remove(action)
        else:
            print("Action not found.")

    def get_event_at_index(self, index):
        try:
            return self._events[index]
        except IndexError:
            print("Index out of range.")

    def remove_event_at_index(self, index):
        try:
            del self._events[index]
        except IndexError:
            print("Index out of range.")

    def get_num_events(self):
        return len(self._events)
