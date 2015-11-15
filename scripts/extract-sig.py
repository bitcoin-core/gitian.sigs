#!/usr/bin/python3
# W.J. van der Laan 2015 (license: MIT)
'''
Extract detached signature from accidentally attached .asc  file
  Example: 
      ./extract-sig.py ./0.10.4rc1-linux/fanquake/bitcoin-linux-0.10-build.assert.asc
  Or:
      find -name \*.asc -print0 | xargs -0 -n 1 ./extract-sig.py

  See https://lists.gnupg.org/pipermail/gnupg-users/2007-June/031414.html
'''
import subprocess
import sys,os,glob
import tempfile,shutil

asc_in = sys.argv[1]
assert(asc_in.endswith('.asc'))
sig_out = asc_in[0:-4] + '.sig'
assert_out = asc_in[0:-4]

tempdir = tempfile.mkdtemp()
try:
    # dearmor, split parts
    with open(asc_in, 'rb') as f:
        sp1 = subprocess.Popen(['gpg','--dearmor'], stdin=f, stdout=subprocess.PIPE)
        sp2 = subprocess.Popen(['gpgsplit','-p',tempdir+'/'], stdin=sp1.stdout)

        sp2.communicate()

    parts = glob.glob(tempdir+'/*')
    sigfile = [x for x in parts if x.endswith('.sig')]
    plainfile = [x for x in parts if x.endswith('.plaintext')]
    assert(len(sigfile)==1 and len(plainfile)==1)

    # copy signature
    shutil.copy(sigfile[0], sig_out)

    # sanitize and copy assert file
    with open(plainfile[0], 'rb') as f: # pipe through gpg to go from --store to plaintext
        sp3 = subprocess.Popen(['gpg'], stdin=f, stdout=subprocess.PIPE)
        (outdata,_) = sp3.communicate()
    # "Edit text_part and remove any whitespace at the end of each line, then remove the LAST (and only the last) message separator (CR, LF, etc)."
    outdata = outdata.rstrip().split(b'\n')
    outdata = [x.rstrip() for x in outdata]
    outdata = b'\n'.join(outdata)
    with open(assert_out, 'wb') as f:
        f.write(outdata)
finally:
    # clean up temorary files and directory
    for x in glob.glob(tempdir+'/*'):
        os.remove(x)
    os.rmdir(tempdir)

