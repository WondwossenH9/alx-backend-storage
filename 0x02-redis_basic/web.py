#!/usr/bin/env python3
"""
Define function `get_page`
"""
import redis
import requests
from datetime import timedelta


def get_page(url: str) -> str:
    """
    Uses requests module to obtain
    HTML content of a particular URL and return it
    Args:
        url (str): url whose content is to be fectched
    Returns:
        html (str): the HTML content of the url
    """
    r = redis.Redis()
    key = "count:{}{}{}".format('{', url, '}')
    r.incr(key)
    res = requests.get(url)
    r.setex(url, timedelta(seconds=10), res.text)
    return res.text
