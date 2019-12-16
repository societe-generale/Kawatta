from typing import Callable


class ComparisonCallbacks:
    def __init__(
        self,
        on_new_item: Callable = None,
        on_delete_item: Callable = None,
        on_update_item: Callable = None,
        on_same_item: Callable = None,
        on_recursion: Callable = None,
    ):
        self.on_new_item = on_new_item
        self.on_delete_item = on_delete_item
        self.on_update_item = on_update_item
        self.on_same_item = on_same_item
        self.on_recursion = on_recursion


class ComparisonFlags:
    def __init__(self, list_index_matters=False):
        self.list_index_matters = list_index_matters


def compare(
    old: dict,
    new: dict,
    callbacks: ComparisonCallbacks,
    flags: ComparisonFlags = None,
    depth=0,
):
    if flags is None:
        flags = ComparisonFlags()
    if isinstance(old, dict) and isinstance(new, dict):
        for key, value in new.items():
            if key in old:
                if (
                    (isinstance(value, dict) and isinstance(old[key], dict))
                    or isinstance(value, (list, tuple))
                    and isinstance(old[key], (list, tuple))
                ):
                    if callbacks.on_recursion:
                        callbacks.on_recursion(key, depth)
                    compare(value, old[key], callbacks, flags, depth + 1)
                elif value == old[key]:
                    if callbacks.on_same_item:
                        callbacks.on_same_item(key, value, depth)
                else:
                    if callbacks.on_update_item:
                        callbacks.on_update_item(key, old[key], value, depth)
            else:
                if callbacks.on_new_item:
                    callbacks.on_new_item(key, value, depth)
        for key, value in old.items():
            if key not in new:
                if callbacks.on_delete_item:
                    callbacks.on_delete_item(key, value, depth)
    elif isinstance(old, (list, tuple)) and isinstance(new, (list, tuple)):
        if flags.list_index_matters:
            compare(
                {k: v for k, v in enumerate(old)},
                {k: v for k, v in enumerate(new)},
                callbacks,
                flags,
                depth,
            )
        else:
            diff_old = [(i, value) for i, value in enumerate(old) if value not in new]
            diff_new = [(i, value) for i, value in enumerate(new) if value not in old]
            nodiff = [
                (i, value) for i, value in enumerate(old) if value not in diff_old
            ] + [(i, value) for i, value in enumerate(new) if value not in diff_new]
            for value in diff_old:
                if callbacks.on_delete_item:
                    callbacks.on_delete_item(value[0], value[1], depth)
            for value in diff_new:
                if callbacks.on_new_item:
                    callbacks.on_new_item(value[0], value[1], depth)
            for value in nodiff:
                if callbacks.on_same_item:
                    callbacks.on_same_item(value[0], value[1], depth)
    else:
        raise RuntimeError(f"Item type mismatch {old} => {new}")
    return callbacks


class StateHolder:
    def __init__(self):
        self.state = {}
        self.path = []
        self.bloc = self.state

    def down(self, key, depth):
        self.select_bloc(depth)
        self.bloc[key] = {}
        self.path.append(key)

    def added_item(self, key, value, depth):
        self.select_bloc(depth)
        self.bloc[key] = ("ADD", value)

    def removed_item(self, key, value, depth):
        self.select_bloc(depth)
        self.bloc[key] = ("DEL", value)

    def modified_item(self, key, old_value, new_value, depth):
        self.select_bloc(depth)
        self.bloc[key] = ("MOD", old_value, new_value)

    def same_item(self, key, value, depth):
        self.select_bloc(depth)
        self.bloc[key] = ("EQL", value)

    def select_bloc(self, depth):
        def recurse_in_path(structure, path):
            if len(path) > 1:
                return recurse_in_path(structure[path[0]], path[1::])
            elif len(path) == 1:
                return structure[path[0]]
            else:
                return structure

        while len(self.path) > depth:
            self.path.pop()
        self.bloc = recurse_in_path(self.state, self.path)


class HumanReadableLogsCallbacks(ComparisonCallbacks):
    def __init__(self, printer=print):
        super().__init__(
            self.on_new_item,
            self.on_delete_item,
            self.on_update_item,
            self.on_same_item,
            self.on_recursion,
        )
        if callable(printer):
            self.printer = printer
        else:
            raise TypeError(f'Expected "printer" to be callable, got {type(printer)}')
        self.state_holder = StateHolder()

    def on_new_item(self, key, value, depth):
        # print(f"{' ' * depth}[+] {key} = {value}")
        self.state_holder.added_item(key, value, depth)

    def on_delete_item(self, key, value, depth):
        # print(f"{' ' * depth}[-] {key} = {value}")
        self.state_holder.removed_item(key, value, depth)

    def on_update_item(self, key, old_value, new_value, depth):
        # print(f"{' ' * depth}[~] {key} = {old_value} => {value}")
        self.state_holder.modified_item(key, old_value, new_value, depth)

    def on_same_item(self, key, value, depth):
        # print(f"{' ' * depth}[=] {key} = {value}")
        self.state_holder.same_item(key, value, depth)

    def on_recursion(self, key, depth):
        # print(f"{' ' * depth}[>] {key}")
        self.state_holder.down(key, depth)

    def print_log(self, filters=["ADD", "MOD", "DEL"]):
        last_path = []

        def display_item(item, path):
            nonlocal last_path

            def get_path_diff(old, new):
                amt = 0
                for i in range(len(old)):
                    if i >= len(new):
                        break
                    elif old[i] == new[i]:
                        amt += 1
                    else:
                        break
                return amt, new[amt::]

            amt_diff, path_diff = get_path_diff(last_path, path)
            if path_diff:
                for i, path_item in enumerate(path_diff):
                    self.printer(f"{' ' * (i + amt_diff)}[>] {path_item}")
                self.printer(f"{' ' * (i + amt_diff + 1)}{item}")
            else:
                self.printer(f"{' ' * (amt_diff)}{item}")
            last_path = path

        def state_walker(state, path, state_filters):
            for k, v in state.items():
                if isinstance(v, dict):
                    state_walker(v, path + [k], state_filters)
                elif isinstance(v, tuple):
                    if v[0] in state_filters:
                        if v[0] == "ADD":
                            display_item(f"[+] {k} = {v[1]}", path)
                        elif v[0] == "MOD":
                            display_item(f"[~] {k} : {v[1]} => {v[2]}", path)
                        elif v[0] == "DEL":
                            display_item(f"[-] {k} = {v[1]}", path)
                        elif v[0] == "EQL":
                            display_item(f"[=] {k} = {v[1]}", path)
                else:
                    raise RuntimeError(
                        f"Unexpected value in state : '{v}' at path '{path}'"
                    )

        state = self.state_holder.state
        state_walker(state, [], filters)


# Usage
"""
callbacks = HumanReadableLogsCallbacks()
compare(
    old_dict,
    new_dict,
    callbacks,
    ComparisonFlags(list_index_matters=True),
)

Equivalence calls:
- callbacks.print_log()
- callbacks.print_log(["ADD", "DEL", "MOD"])
"""
