""" Use eea.cache for LDAP caching instead of bugous Products.MemcachedManager

See #94988
"""

import hashlib
from eea.cache import cache


def sha_cachekey(sig):
    return hashlib.sha256(str(sig)).hexdigest()


def _cachekey_lookupuserbyattr(meth, self, *args, **kwargs):
    sig = (meth.__name__, self.__name__, args, kwargs.items())
    return sha_cachekey(sig)


@cache(_cachekey_lookupuserbyattr)
def _lookupuserbyattr_cache_wrapper(meth, *args, **kwargs):
    """ Wrapper to raise error when login was not successfull.
        Needed to avoid caching unsuccessfull login attempts.
    """
    result = meth(*args, **kwargs)
    if not any(result):
        raise ValueError(result)
    return result


def _lookupuserbyattr(self, *args, **kwargs):
    try:
        return _lookupuserbyattr_cache_wrapper(
            self._old__lookupuserbyattr, *args, **kwargs)
    except ValueError as exc:
        return exc.message


def _cachekey_LDAPDelegate_search(meth, self, *args, **kwargs):
    kw = tuple([(k, v) for k, v in kwargs.items() if k != 'bind_pwd'])
    sig = (meth.__name__, self.__name__, args, kw)
    return sha_cachekey(sig)


@cache(_cachekey_LDAPDelegate_search)
def LDAPDelegate_search_cache_wrapper(meth, *args, **kwargs):
    """ Wrapper to avoid cache when there is an
        error in the query result.
    """
    result = meth(*args, **kwargs)

    if result['exception']:
        raise ValueError(result)

    return result


def LDAPDelegate_search(self, *args, **kwargs):
    try:
        return LDAPDelegate_search_cache_wrapper(
            self._old_search, *args, **kwargs)
    except ValueError as exc:
        return exc.message
