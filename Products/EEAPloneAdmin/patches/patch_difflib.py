""" difflib
"""

def _line_wrapper(self,diffs):
    """Returns iterator that splits (wraps) mdiff text lines"""

    # pull from/to data and flags from mdiff iterator
    for fromdata,todata,flag in diffs:
        # check for context separators and pass them through
        if flag is None:
            yield fromdata,todata,flag
            continue
        (fromline,fromtext),(toline,totext) = fromdata,todata
        # for each from/to line split it at the wrap column to form
        # list of text lines.
        fromlist,tolist = [],[]
        try:
            self._split_line(fromlist,fromline,fromtext)
        except RuntimeError:
            fromlist = []
            _iterative_split_line(self, fromlist, fromline, fromtext)
        try:
            self._split_line(tolist,toline,totext)
        except RuntimeError:
            tolist = []
            _iterative_split_line(self,tolist, toline, totext)
        # yield from/to line in pairs inserting blank lines as
        # necessary when one side has more wrapped lines
        while fromlist or tolist:
            if fromlist:
                fromdata = fromlist.pop(0)
            else:
                fromdata = ('',' ')
            if tolist:
                todata = tolist.pop(0)
            else:
                todata = ('',' ')
            yield fromdata,todata,flag
 
def _iterative_split_line(self,data_list,line_num,text):
    """
    Has the same result as the original _split_line but it's an iterative 
    algorithm instead of a recursive one. 
    """
    # if blank line or context separator, just add it to the output list

    while True:
        if not line_num:
            data_list.append((line_num,text))
            #return
            break
        
        # if line text doesn't need wrapping, just add it to the output list
        size = len(text)
        max = self._wrapcolumn
        if (size <= max) or ((size -(text.count('\0')*3)) <= max):
            data_list.append((line_num,text))
            #return
            break
    
        # scan text looking for the wrap point, keeping track if the wrap
        # point is inside markers
        i = 0
        n = 0
        mark = ''
        while n < max and i < size:
            if text[i] == '\0':
                i += 1
                mark = text[i]
                i += 1
            elif text[i] == '\1':
                i += 1
                mark = ''
            else:
                i += 1
                n += 1
        
        # wrap point is inside text, break it up into separate lines
        line1 = text[:i]
        line2 = text[i:]
        
        # if wrap point is inside markers, place end marker at end of first
        # line and start marker at beginning of second line because each
        # line will have its own table tag markup around it.
        if mark:
            line1 = line1 + '\1'
            line2 = '\0' + mark + line2
        
        # tack on first line onto the output list
        data_list.append((line_num,line1))

        line_num = '>'
        text = line2
