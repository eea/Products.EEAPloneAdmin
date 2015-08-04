""" Removing 'zc.async' left over from old single database configuration
"""
import transaction


def remove_old_async(context):
	context._p_jar.root().pop('zc.async')
	transaction.commit()
