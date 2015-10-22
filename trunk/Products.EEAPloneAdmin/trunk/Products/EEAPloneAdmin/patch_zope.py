""" Patches for Zope package
"""
from OFS.CopySupport import *
from OFS.CopySupport import _cb_decode

def manage_pasteObjects(self, cb_copy_data=None, REQUEST=None):
    """Paste previously copied objects into the current object.

    If calling manage_pasteObjects from python code, pass the result of a
    previous call to manage_cutObjects or manage_copyObjects as the first
    argument.

    Also sends IObjectCopiedEvent and IObjectClonedEvent
    or IObjectWillBeMovedEvent and IObjectMovedEvent.
    """
    ### due to the ticket #14598: the need to also handle a cb_copy_data
    ### structure that contains the desired new id on a copy/paste operation.
    ### this feature will be used when creating a new version for an object.
    ### if there is no new id also incapsulated in the cb_copy_data then
    ### the copy/paste will work as default.
    ### also the cut/paste remains the same.
    if cb_copy_data is not None:
        cp = cb_copy_data
    elif REQUEST is not None and REQUEST.has_key('__cp'):
        cp = REQUEST['__cp']
    else:
        cp = None
    if cp is None:
        raise CopyError(eNoData)

    try:
        op, mdatas, newids = _cb_decode(cp)
    except:
        try:
            op, mdatas = _cb_decode(cp)
            newids = []
        except:
            raise CopyError(eInvalid)
    else:
        if len(mdatas)!=len(newids):
            raise CopyError(eInvalid)

    oblist = []
    app = self.getPhysicalRoot()
    for mdata in mdatas:
        m = loadMoniker(mdata)
        try:
            ob = m.bind(app)
        except ConflictError:
            raise
        except:
            raise CopyError(eNotFound)
        self._verifyObjectPaste(ob, validate_src=op+1)
        oblist.append(ob)

    if len(newids)==0:
        newids = ['']*len(oblist)

    result = []
    if op == 0:
        # Copy operation
        for ob, new_id in zip(oblist, newids):
            orig_id = ob.getId()
            if not ob.cb_isCopyable():
                raise CopyError(eNotSupported % escape(orig_id))

            try:
                ob._notifyOfCopyTo(self, op=0)
            except ConflictError:
                raise
            except:
                raise CopyError(MessageDialog(
                    title="Copy Error",
                    message=sys.exc_info()[1],
                    action='manage_main'))

            if new_id != '':
                id = new_id
            else:
                id = self._get_id(orig_id)
            result.append({'id': orig_id, 'new_id': id})

            orig_ob = ob
            ob = ob._getCopy(self)
            ob._setId(id)
            notify(ObjectCopiedEvent(ob, orig_ob))

            self._setObject(id, ob)
            ob = self._getOb(id)
            ob.wl_clearLocks()

            ob._postCopy(self, op=0)

            compatibilityCall('manage_afterClone', ob, ob)

            notify(ObjectClonedEvent(ob))

        if REQUEST is not None:
            return self.manage_main(self, REQUEST, update_menu=1,
                                    cb_dataValid=1)

    elif op == 1:
        # Move operation
        for ob in oblist:
            orig_id = ob.getId()
            if not ob.cb_isMoveable():
                raise CopyError(eNotSupported % escape(orig_id))

            try:
                ob._notifyOfCopyTo(self, op=1)
            except ConflictError:
                raise
            except:
                raise CopyError(MessageDialog(
                    title="Move Error",
                    message=sys.exc_info()[1],
                    action='manage_main'))

            if not sanity_check(self, ob):
                raise CopyError(
                        "This object cannot be pasted into itself")

            orig_container = aq_parent(aq_inner(ob))
            if aq_base(orig_container) is aq_base(self):
                id = orig_id
            else:
                id = self._get_id(orig_id)
            result.append({'id': orig_id, 'new_id': id})

            notify(ObjectWillBeMovedEvent(ob, orig_container, orig_id,
                                          self, id))

            # try to make ownership explicit so that it gets carried
            # along to the new location if needed.
            ob.manage_changeOwnershipType(explicit=1)

            try:
                orig_container._delObject(orig_id, suppress_events=True)
            except TypeError:
                orig_container._delObject(orig_id)
                warnings.warn(
                    "%s._delObject without suppress_events is discouraged."
                    % orig_container.__class__.__name__,
                    DeprecationWarning)
            ob = aq_base(ob)
            ob._setId(id)

            try:
                self._setObject(id, ob, set_owner=0, suppress_events=True)
            except TypeError:
                self._setObject(id, ob, set_owner=0)
                warnings.warn(
                    "%s._setObject without suppress_events is discouraged."
                    % self.__class__.__name__, DeprecationWarning)
            ob = self._getOb(id)

            notify(ObjectMovedEvent(ob, orig_container, orig_id, self, id))
            notifyContainerModified(orig_container)
            if aq_base(orig_container) is not aq_base(self):
                notifyContainerModified(self)

            ob._postCopy(self, op=1)
            # try to make ownership implicit if possible
            ob.manage_changeOwnershipType(explicit=0)

        if REQUEST is not None:
            REQUEST['RESPONSE'].setCookie('__cp', 'deleted',
                                path='%s' % cookie_path(REQUEST),
                                expires='Wed, 31-Dec-97 23:59:59 GMT')
            REQUEST['__cp'] = None
            return self.manage_main(self, REQUEST, update_menu=1,
                                    cb_dataValid=0)

    return result
