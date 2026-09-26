mkdir -p ~/.ssh && chmod 700 ~/.ssh
[ -f ~/.ssh/jenkins_devtools ] || ssh-keygen -q -t ed25519 -N '' -C jenkins-to-devtools -f ~/.ssh/jenkins_devtools
touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
grep -qxF "$(cat ~/.ssh/jenkins_devtools.pub)" ~/.ssh/authorized_keys || cat ~/.ssh/jenkins_devtools.pub >> ~/.ssh/authorized_keys
ssh-keygen -lf ~/.ssh/jenkins_devtools.pub
grep -c jenkins-to-devtools ~/.ssh/authorized_keys
