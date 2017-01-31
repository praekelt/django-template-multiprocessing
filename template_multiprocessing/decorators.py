def multiprocess(klass):
    """
    A decorator that defines the __html__ method. This helps non-Django
    templates to detect classes whose __str__ methods return SafeText.
    """
    setattr(klass, '__multiprocess_safe__', True)
    return klass
