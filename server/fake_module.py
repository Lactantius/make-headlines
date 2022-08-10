import sys
from types import ModuleType


class ModuleSpec:
    """Dummy ModuleSpec class"""

    def __init__(self, name):
        self.name = name

    def origin(self):
        return f"Origin of {self} is fake_module."

    def has_location(self):
        return f"{self} has no true location"


# ModuleSpec(name, loader, *, origin=None, loader_state=None, is_package=None)


def new_module(name: str, doc=None):
    """
    Make fake modules.
    From https://stackoverflow.com/a/27476659/6632828
    """

    m = ModuleType(name, doc)
    m.__file__ = name + ".py"
    m.__spec__ = ModuleSpec(name)
    m.__repr__ = f"Fake module: {name}"
    if m.__file__ != "cuda.py":
        m.cuda = new_module("cuda")
    m.is_available = lambda: True
    m.origin = "Fake"
    m.device = lambda device: device
    sys.modules[name] = m
    return m
