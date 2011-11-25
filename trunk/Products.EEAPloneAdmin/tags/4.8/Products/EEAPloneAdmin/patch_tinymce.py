from Acquisition import aq_base 
from Products.Archetypes.interfaces import IBaseObject

def patched_getContentType(self, object=None, fieldname=None):                                                                                                                                     
    """Original code here. Notice that it doesn't treat properly the case that fieldname is None

    def getContentType(self, object=None, fieldname=None):
        context = aq_base(object)
        if IBaseObject.providedBy(context):
            # support Archetypes fields
            if fieldname is None:
                field = context.getPrimaryField()
            else:
                field = context.getField(fieldname) or getattr(context, fieldname, None)
            if field and hasattr(aq_base(field), 'getContentType'):
                return field.getContentType(context)
        elif '.widgets.' in fieldname:
            # support plone.app.textfield RichTextValues
            fieldname = fieldname.split('.widgets.')[-1]
            field = getattr(context, fieldname, None)
            mimetype = getattr(field, 'mimeType', None)
            if mimetype is not None:
                return mimetype
        return 'text/html'
    """

    context = aq_base(object)                                                                                                                                                              
    if IBaseObject.providedBy(context):                                                                                                                                                    
        # support Archetypes fields                                                                                                                                                        
        if fieldname is None:                                                                                                                                                              
            field = context.getPrimaryField()                                                                                                                                              
        else:                                                                                                                                                                              
            field = context.getField(fieldname) or getattr(context, fieldname, None)                                                                                                       
        if field and hasattr(aq_base(field), 'getContentType'):                                                                                                                            
            return field.getContentType(context)                                                                                                                                           
    elif fieldname == None:                                                                                                                                                                
        return 'text/html'                                                                                                                                                                 
    elif '.widgets.' in fieldname:                                                                                                                                                         
        # support plone.app.textfield RichTextValues                                                                                                                                       
        fieldname = fieldname.split('.widgets.')[-1]                                                                                                                                       
        field = getattr(context, fieldname, None)                                                                                                                                          
        mimetype = getattr(field, 'mimeType', None)                                                                                                                                        
        if mimetype is not None:                                                                                                                                                           
            return mimetype                                                                                                                                                                
    return 'text/html'     
