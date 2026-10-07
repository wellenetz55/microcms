"""Transfer to a private staging directory over SSH, then publish verified files."""
import argparse
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import subprocess
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('--release',type=Path,required=True)
parser.add_argument('--apply',action='store_true',help='Without this, transfer + server-side dry run only')
args = parser.parse_args()
host, user, root = (os.environ.get(n,'') for n in ('XSERVER_HOST','XSERVER_USER','XSERVER_PUBLIC_DIR'))
if not re.fullmatch(r'[A-Za-z0-9.-]+',host) or not re.fullmatch(r'[A-Za-z0-9_-]+',user): raise SystemExit('Configure XSERVER_HOST and XSERVER_USER')
if not re.fullmatch(r'/home/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/public_html(?:/[A-Za-z0-9_-]+)?',root):
    raise SystemExit('XSERVER_PUBLIC_DIR must be /home/USER/DOMAIN/public_html or one preview subdirectory')
key, known = (os.environ.get(n,'') for n in ('XSERVER_KEY_FILE','XSERVER_KNOWN_HOSTS_FILE'))
if not Path(key).is_file() or not Path(known).is_file(): raise SystemExit('SSH key / verified known_hosts file missing')
ssh = ['ssh','-p','10022','-i',key,'-o','BatchMode=yes','-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+known]
target = user+'@'+host
# Separate state for each destination; outside public_html, never publicly downloadable.
public_root = str(PurePosixPath(root).parents[0]) if root.endswith('/public_html') else str(PurePosixPath(root).parents[1])
state = public_root+'/.wellenetz-cms-'+PurePosixPath(root).name
stage = state+'/incoming/'+uuid.uuid4().hex

def remote(argv): subprocess.run(ssh+[target,shlex.join(argv)],check=True)
remote(['python3','--version'])
remote(['mkdir','-p',stage])
try:
    subprocess.run(['rsync','-az','-e',shlex.join(ssh),str(args.release.resolve())+'/',target+':'+stage+'/'],check=True)
    subprocess.run(['rsync','-az','-e',shlex.join(ssh),str(Path(__file__).with_name('publish.py')),target+':'+stage+'/publish.py'],check=True)
    command = ['python3',stage+'/publish.py','--release',stage,'--root',root,'--state',state]
    if not args.apply: command.append('--dry-run')
    remote(command)
finally:
    # Only the unique staging directory created by this run is removed.
    remote(['rm','-rf','--',stage])
