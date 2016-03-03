def list_all():
    import os
    moduledir = os.path.dirname(__file__)
    plugins = filter(lambda x:
                     x.startswith("Effect_") and
                     x.endswith(".py") and
                     os.path.isfile(os.path.join(moduledir,x)),
                     os.listdir(moduledir))
    return [ i[7:-3] for i in plugins ]

def load(name):
    import imp, os
    moduledir  = os.path.dirname(__file__)
    modulename = "Effect_"+name
    fp, pathname, description = imp.find_module(modulename,[moduledir])
    return imp.load_module("EffectInstance", fp, pathname, description)
