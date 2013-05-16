#coding: utf8
from django.db import transaction


def nested_commit_on_success(func):
    """Like commit_on_success, but doesn't commit existing transactions.

        This decorator is used to run a function within the scope of a 
        database transaction, committing the transaction on success and
        rolling it back if an exception occurs.

        Unlike the standard transaction.commit_on_success decorator, this
        version first checks whether a transaction is already active.  If so
        then it doesn't perform any commits or rollbacks, leaving that up to
        whoever is managing the active transaction. """
    commit_on_success = transaction.commit_on_success(func)
    def _nested_commit_on_success(*args, **kwds):
        if transaction.is_managed():
            return func(*args,**kwds)
        else:
            return commit_on_success(*args,**kwds)
    return transaction.wraps(func)(_nested_commit_on_success)

