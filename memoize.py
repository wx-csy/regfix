from functools import wraps

def memoize(method) :
    memo = dict()
    @wraps(method)
    def _impl(*args) :
        if args not in memo :
            memo[args] = method(*args)
        return memo[args]
    return _impl
        

def memoize_property(func) :
    return property(memoize(func))