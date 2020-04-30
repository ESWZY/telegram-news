# -*- coding: UTF-8 -*-

"""
Rate limit decorator for API request limit.

This module includes the decorator used to rate limit function invocations.
Additionally this module includes a naive retry strategy to be used in
conjunction with the rate limit decorator. Modified from ratelimit==2.1.1.

However, the API documentation has not many detail. Some possible rate:
For channel, 20 per 60 seconds and 1 per 1 second are possible limit rate.

In my experiment, a better result for no 429 error is once per 3 seconds.
But, if you want to post messages as soon as possible, not using rate limit
decorator is the most fast way.
"""

import sys
import threading
import time
from functools import wraps
from math import floor


class RateLimitException(Exception):
    """Created exception class for rate limit occurrences."""

    def __init__(self, message, period_remaining):
        """
        Add message and remaining time.

        When the number of function invocations exceeds the rate limit.
        Additionally the exception has the remaining time period after which
        the rate limit is reset.

        :param string message: Custom exception message.
        :param float period_remaining: The time remaining until the rate limit is reset.
        """
        super(RateLimitException, self).__init__(message)
        self.period_remaining = period_remaining


def now():
    """
    Get the current time function.

    :return: Time function.
    :rtype: function
    """
    if hasattr(time, 'monotonic'):
        return time.monotonic
    return time.time


class RateLimitDecorator(object):
    """Rate limit decorator class."""

    def __init__(self, calls=8, period=10, clock=now()):
        """
        Instantiate a RateLimitDecorator with some sensible defaults.

        :param int calls: Maximum function invocations allowed within a time period.
        :param float period: An upper bound time period (in seconds) before the rate limit resets.
        :param function clock: An optional function retuning the current time.
        """
        self.clamped_calls = max(1, min(sys.maxsize, floor(calls)))
        self.period = period
        self.clock = clock

        # Initialise the decorator state.
        self.last_reset = clock()
        self.num_calls = 0

        # Add thread safety.
        self.lock = threading.RLock()

    def __call__(self, func):
        """
        Return a wrapped function that prevents further function invocations.

        :param function func: The decorated function.
        """

        @wraps(func)
        def wrapper(*args, **kargs):
            """
            Extend the behaviour of the decorated function.

            Forwarding function invocations previously called no sooner than
            a specified period of time. The decorator will raise an exception
            if the function cannot be called.

            :param args: non-keyword variable length argument list to the decorated function.
            :param kargs: keyword variable length argument list to the decorated function.
            :raises: RateLimitException
            """
            with self.lock:
                period_remaining = self.__period_remaining()

                # If the time window has elapsed then reset.
                if period_remaining <= 0:
                    self.num_calls = 0
                    self.last_reset = self.clock()

                # Increase the number of attempts to call the function.
                self.num_calls += 1

                # If the number of attempts to call the function exceeds the
                # maximum then raise an exception.
                if self.num_calls > self.clamped_calls:
                    raise RateLimitException('too many calls', period_remaining)

            return func(*args, **kargs)

        return wrapper

    def __period_remaining(self):
        """
        Return the period remaining for the current rate limit window.

        :return: The remaining period.
        :rtype: float
        """
        elapsed = self.clock() - self.last_reset
        return self.period - elapsed


def sleep_and_retry(func):
    """
    Return a wrapped function that rescues rate limit exceptions.

    Sleep the current thread until rate limit resets.

    :param function func: The function to decorate.
    :return: Decorated function.
    :rtype: function
    """

    @wraps(func)
    def wrapper(*args, **kargs):
        """
        Call the rate limited function, when the function raises a rate limit.

        :param args: non-keyword variable length argument list to the decorated function.
        :param kargs: keyword variable length argument list to the decorated function.
        """
        while True:
            try:
                return func(*args, **kargs)
            except RateLimitException as exception:
                time.sleep(exception.period_remaining)

    return wrapper
