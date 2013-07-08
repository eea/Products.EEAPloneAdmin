"""script to symlink maildrop 
"""

import os.path
import subprocess
import Products.MaildropHost.maildrop.maildrop as md
import sys


MAILDROP = 'maildrop'

def link():
    """symlink maildrop script
    """
    if len(sys.argv) != 2:
        raise ValueError("Need path to buildout 'bin' folder as argument")

    bin_folder = sys.argv[1]
    dest = os.path.abspath(os.path.join(bin_folder, MAILDROP))
    source = md.__file__
    if source.endswith('.pyc'):
        source = source[:-1]
    cmd = ['ln', '-s', source, dest]
    subprocess.check_call(cmd, cwd=bin_folder)
    print "Created link to maildrop at", dest
