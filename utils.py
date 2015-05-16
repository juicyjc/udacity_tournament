#!/usr/bin/env python
#
# utils.py - utilities for tournament.py
#


def tuple_without(original_tuple, element_to_remove):
    """Removes an element from a tuple.

    This function was found online:
    http://www.markhneedham.com/blog/2013/01/27/python-conceptually-
    removing-an-item-from-a-tuple/

    Args:
      original_tuple: the complete tuple
      element_to_remove: the element of the tuple to remove

    Returns:
      The tuple minus the element to remove
    """
    return filter(lambda el: el != element_to_remove, original_tuple)
