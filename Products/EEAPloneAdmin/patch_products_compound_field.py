""" 84611 allow setting of empty datetimes
"""
import types
from Products.CompoundField import config
ListTypes = (types.TupleType, types.ListType)
import logging

log = logging.getLogger()


def set(self, instance, value, **kwargs):
    if not value:
        return

    # keep evil eval for BBB, but: its a security hole
    # disabled by default
    if config.EVIL_EVAL and type(value) in types.StringTypes:
        #if the value comes as string eval it to a dict
        # XXX attention: use restricted environment instead!
        # this is a potential security hole.
        value = eval(value)

    if getattr(self, 'value_class', None):
        if isinstance(value, self.value_class):
            value = self.valueClass2Raw(value)

    for f in self.Schema().fields():
        if value.has_key(f.old_name):
            v = value[f.old_name]
            isarray = type(v) in ListTypes and len(v)==2 and type(v[1]) == types.DictType
            if v and isarray:
                kw=v[1]
            else:
                kw={}

            request = instance.REQUEST
            if (v or \
                f.type == 'lines' and \
                not ('controller_state' in request and \
                     request['controller_state'].getErrors())):
                if isarray or (type(v) in ListTypes and len(v) ==1) and f.type != 'datagrid':
                    f.set(instance, v[0], **kw)
                else:
                    f.set(instance, v, **kw)
            #### eea patch allow setting of empty values if we have a datetime
            log.info('called it david')
            if not v and f.type == 'datetime':
                f.set(instance, v, **kw)