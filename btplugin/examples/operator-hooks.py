import operator

#def class_hooks(cls):
#  return [name for name in dir(cls)]

import operator
operator_hooks = [name for name in dir(operator)]

def instrument_operator_hooks(cls):
    def add_hook(name):
        operator_func = getattr(operator, name.strip('_'), None)
        existing = getattr(cls, name, None)

        def op_hook(self, *args, **kw):
            print "Hooking into {}".format(name)
            self._function = operator_func
            self._params = (args, kw)
            if existing is not None:
                return existing(self, *args, **kw)
            raise AttributeError(name)

        try:
            setattr(cls, name, op_hook)
        except (AttributeError, TypeError):
            pass  # skip __name__ and __doc__ and the like

    for hook_name in operator_hooks:
        add_hook(hook_name)
    return cls

def CatchAllType(*args, **kwargs):
    base_class = kwargs.pop("base_class",None)
    @instrument_operator_hooks
    class CatchAll(base_class):
        pass
    return type(CatchAll(*args,**kwargs))

c = CatchAllType(["one", "two", "three"], base_class=str)
print dir(c)

print c
#c.append("bar")
#f = ["hello"]
#print c+f
