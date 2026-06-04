# enigma_engine.py

class EnigmaEngine:
    # Historical wiring mappings for Rotors I-IX and Reflector B
    # To change the order of a rotor, just rearrange the 26 letters inside the quotes!
    ROTORS = {
        "I":    "EKMFLGDQVZNTOWYHXUSPAIBRCJ",
        "II":   "AJDKSIRUXBLHWTMCQGZNPYFVOE",
        "III":  "BDFHJLCPRTXVZNYEIWGAKMUSQO",
        "IV":   "ESOVPZJAYQUIRHXLNFTGKDCMWB",
        "V":    "VZBRGITYUPSDNHLXAWMJQOFECK",
        "VI":   "JPGVOUMFYQBENHZRDKASXLICTW", # Historical M3/M4 Rotor
        "VII":  "NZJHGRCXMYSWBOUFAIVLPEKQDT", # Historical M3/M4 Rotor
        "VIII": "FKQHTLXOCBJSPDZRAMEWNIUYGV", # Historical M3/M4 Rotor
        "IX":   "LEYJVCNIXWPBQMDRTAKZGFUHOS"  # Historical 'Beta' Rotor
    }
    REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def __init__(self, selected_rotors, initial_key):
        self.r1_wire = self.ROTORS[selected_rotors[0]]
        self.r2_wire = self.ROTORS[selected_rotors[1]]
        self.r3_wire = self.ROTORS[selected_rotors[2]]
        
        self.p1 = self.ALPHABET.index(initial_key[0].upper()) # Left
        self.p2 = self.ALPHABET.index(initial_key[1].upper()) # Middle
        self.p3 = self.ALPHABET.index(initial_key[2].upper()) # Right
        
        self.plugboard = {}

    def step_rotors(self):
        """Steps the rotors. Right rotor steps every time."""
        self.p3 = (self.p3 + 1) % 26
        if self.p3 == 0:
            self.p2 = (self.p2 + 1) % 26
            if self.p2 == 0:
                self.p1 = (self.p1 + 1) % 26

    def _pass_forward(self, index, wire, position):
        shifted_in = (index + position) % 26
        char_out = wire[shifted_in]
        return (self.ALPHABET.index(char_out) - position) % 26

    def _pass_backward(self, index, wire, position):
        shifted_in = (index + position) % 26
        char_in = self.ALPHABET[shifted_in]
        char_out_index = wire.index(char_in)
        return (char_out_index - position) % 26

    def encrypt_char(self, char):
        char = char.upper()
        
        if char not in self.ALPHABET:
            return char  

        self.step_rotors()

        char = self.plugboard.get(char, char)
        idx = self.ALPHABET.index(char)

        idx = self._pass_forward(idx, self.r3_wire, self.p3)
        idx = self._pass_forward(idx, self.r2_wire, self.p2)
        idx = self._pass_forward(idx, self.r1_wire, self.p1)

        idx = self.ALPHABET.index(self.REFLECTOR_B[idx])

        idx = self._pass_backward(idx, self.r1_wire, self.p1)
        idx = self._pass_backward(idx, self.r2_wire, self.p2)
        idx = self._pass_backward(idx, self.r3_wire, self.p3)

        out_char = self.ALPHABET[idx]
        return self.plugboard.get(out_char, out_char)