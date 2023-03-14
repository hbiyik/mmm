from . import allwinner_a33
from libmmm import model
import inspect


def getdevices(mod):
    for attr in dir(mod):
        attr_type = getattr(mod, attr)
        if inspect.isclass(attr_type) and issubclass(attr_type, model.Device) and attr_type is not model.Device:
            yield attr_type
    
catalogs = {"a33": list(getdevices(allwinner_a33))}