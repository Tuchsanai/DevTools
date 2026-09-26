#!/usr/bin/env python3
"""Run the README ssh-test block (docker exec -it jenkins ssh ... root@devtools hostname) in a real pty,
type the password from env LAB_SSH_PASS at the prompt like a learner would, and print the transcript.
Usage: pty_ssh.py <block file> <jenkins container name>. Owner: yolo3."""
import os, pty, select, shlex, sys, time
cmd = shlex.split(open(sys.argv[1]).read().strip())
assert cmd[:3] == ['docker', 'exec', '-it'] and cmd[3] == 'jenkins', cmd
cmd[3] = sys.argv[2]
pid, fd = pty.fork()
if pid == 0:
    os.execvp(cmd[0], cmd)
buf, sent, end = b'', False, time.time() + 40
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 1)
    if fd not in r:
        continue
    try:
        d = os.read(fd, 1024)
    except OSError:
        break
    if not d:
        break
    buf += d
    if not sent and buf.rstrip().endswith(b'password:'):
        os.write(fd, (os.environ['LAB_SSH_PASS'] + '\n').encode()); sent = True
_, st = os.waitpid(pid, 0)
out = buf.decode(errors='replace').replace('\r\n', '\n').replace('\r', '')
assert os.environ['LAB_SSH_PASS'] not in out.replace("password:", "")
print(out.rstrip('\n')); print(f'[exit={os.waitstatus_to_exitcode(st)} password_typed={sent}]')
