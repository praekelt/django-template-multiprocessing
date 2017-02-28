def multiprocess(predicate=None, after_render=None, callback=None):
    def inner(klass):
        setattr(klass, "__multiprocess_safe__", True)
        setattr(klass, "__multiprocess_predicate__", predicate)
        setattr(klass, "__multiprocess_after_render", after_render)
        setattr(klass, "__multiprocess_callback", callback)
        return klass
    return inner
