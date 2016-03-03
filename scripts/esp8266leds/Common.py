import argparse

def arg_range(first,last,arg_type=int):
    def f(string):
        value = arg_type(string)
        if value < first or value > last:
            raise argparse.ArgumentTypeError(
                "value out of range: %s < value < %s" %
                (str(first),str(last)))
        return value
    return f

def arg_positive(arg_type=int):
    def f(string):
        value = arg_type(string)
        if value < 0:
            raise argparse.ArgumentTypeError("value must be positive")
        return value
    return f
