class OceanPersonality:
    def __init__(self):
        self._O = 1.0
        self._C = 1.0
        self._E = 1.0
        self._A = 1.0
        self._N = 1.0

    def init(self, attributes_dict):
        required_keys = {'O', 'C', 'E', 'A', 'N'}
        if not required_keys.issubset(attributes_dict.keys()):
            raise ValueError("Dictionary must contain all required keys: O, C, E, A, N")

        self._O = attributes_dict['O']
        self._C = attributes_dict['C']
        self._E = attributes_dict['E']
        self._A = attributes_dict['A']
        self._N = attributes_dict['N']

    def get_O(self):
        return self._O

    def set_O(self, value):
        self._O = value

    def get_C(self):
        return self._C

    def set_C(self, value):
        self._C = value

    def get_E(self):
        return self._E

    def set_E(self, value):
        self._E = value

    def get_A(self):
        return self._A

    def set_A(self, value):
        self._A = value

    def get_N(self):
        return self._N

    def set_N(self, value):
        self._N = value