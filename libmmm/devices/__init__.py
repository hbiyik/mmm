from libmmm import model
from . import rk3588
from . import allwinner_a33
import inspect


def getdevices(mod):
    for attr in dir(mod):
        attr_type = getattr(mod, attr)
        if inspect.isclass(attr_type) and issubclass(attr_type, model.Device) and attr_type is not model.Device:
            yield attr_type


catalogs = {"a33": list(getdevices(allwinner_a33)),
            "rk3588": list(getdevices(rk3588))}
