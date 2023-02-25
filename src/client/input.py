import json
import os

from src.log import log, warn


class Bool:
    def __init__(self, val: bool):
        self.val = val

    def true(self): print('t'); self.val = True
    def false(self): self.val = False


class InputManager:
    def __init__(self, instance, keymaps_file: str):
        self.instance = instance
        self.keymaps = self.load_keymaps(file=keymaps_file)

    def load_keymaps(self, file: str):
        log("Loading keymaps.", "Worker/InputManager")
        with open(file, "r") as fp:
            key_data: dict = json.load(fp=fp)
            for action in key_data:
                key_data[action] = {
                    "key": key_data[action],
                    "fn_assigned": None,
                    "state": Bool(False),
                }

                print(key_data[action])

                self.instance.accept(
                    key_data[action]["key"], key_data[action]["state"].true)
                self.instance.accept(
                    key_data[action]["key"], key_data[action]["state"].false)

            print("KEY_DATA: ", key_data)
            return key_data

    def listen(self, action: str, fn: callable) -> None:
        if action not in self.keymaps:
            return

        self.keymaps[action]["fn_assigned"] = fn
        return self.instance.accept(self.keymaps[action]["key"], fn)

    def get_state(self, action: str) -> str | None:
        """
        Get whether this key is pressed or not.
        """
        if action in self.keymaps:
            return self.keymaps[action]["state"]

        raise ValueError("Invalid action: {}".format(action))
