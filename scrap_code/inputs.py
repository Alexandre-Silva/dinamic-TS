#Python3 has only input that return a string
    >>> user_input = input('Give me a number: ')
    Give me a number: 10
    >>> user_input
    '10'
    >>> type(user_input)
    <class 'str'>
    >>> print 'Your number was %s' % (user_input)
    SyntaxError: invalid syntax (<pyshell#4>, line 1)
    >>> print ('Your number was %s' % (user_input))
    Your number was 10
    >>> #And print has become function print()
    >>>
