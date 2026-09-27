#!/usr/bin/env python3
"""Create folder 'verify-local' with FOLDER-scoped credentials (global store stays empty for the
coordinator's screenshots) and two SCM jobs inside it:
  - upstream-main     : Git https://github.com/Tuchsanai/DevTools.git */main (read-only upstream compatibility)
  - local-jenkinsfile : local bare repo holding the modified Jenkinsfile (never pushed anywhere)"""
import base64, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import jk

SP = '04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile'
b64 = lambda s: base64.b64encode(s.encode()).decode()
dec = lambda s: f"new String(Base64.decoder.decode('{b64(s)}'), 'UTF-8')"

groovy = f'''
import com.cloudbees.hudson.plugins.folder.Folder
import com.cloudbees.hudson.plugins.folder.properties.FolderCredentialsProvider.FolderCredentialsProperty
import com.cloudbees.plugins.credentials.CredentialsScope
import com.cloudbees.plugins.credentials.domains.Domain
import com.cloudbees.plugins.credentials.domains.DomainCredentials
import com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl
def j = jenkins.model.Jenkins.get()
def f = j.getItem('verify-local') ?: j.createProject(Folder, 'verify-local')
f.description = 'Task-owned validation folder (credentials scoped here, not global)'
def prop = f.properties.get(FolderCredentialsProperty)
if (!prop) {{ prop = new FolderCredentialsProperty([] as DomainCredentials[]); f.addProperty(prop) }}
def store = prop.store
[['devtools-ssh', 'root', {dec('passwd')}, 'SSH password: Jenkins to devtools'],
 ['dockerhub', {dec(os.environ['DOCKER_USER'])}, {dec(os.environ['DOCKER_TOKEN'])}, 'Docker Hub access token']].each {{ c ->
  def cred = new UsernamePasswordCredentialsImpl(CredentialsScope.GLOBAL, c[0], c[3], c[1], c[2])
  def ex = store.getCredentials(Domain.global()).find {{ it.id == c[0] }}
  if (ex) store.updateCredentials(Domain.global(), ex, cred) else store.addCredentials(Domain.global(), cred)
}}
f.save()
println "folder creds: " + store.getCredentials(Domain.global()).collect {{ it.id }}
println "global creds: " + com.cloudbees.plugins.credentials.SystemCredentialsProvider.instance.credentials.collect {{ it.id }}
'''
st, out, _ = jk.script(groovy)
print(st, jk.redact(out).strip())

PARAMS = [('GIT_URL', 'https://github.com/Tuchsanai/DevTools.git'), ('GIT_REF', 'main'),
          ('APP_SUBDIR', '04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop'),
          ('APP_VERSION', '1.0.0'), ('TAG_PREFIX', 'lab3')]


def job_xml(url, desc):
    params = ''.join(f'<hudson.model.StringParameterDefinition><name>{n}</name><defaultValue>{v}</defaultValue>'
                     f'<trim>false</trim></hudson.model.StringParameterDefinition>' for n, v in PARAMS)
    return f'''<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job">
  <description>{desc}</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.ParametersDefinitionProperty><parameterDefinitions>{params}</parameterDefinitions></hudson.model.ParametersDefinitionProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps">
    <scm class="hudson.plugins.git.GitSCM" plugin="git">
      <configVersion>2</configVersion>
      <userRemoteConfigs><hudson.plugins.git.UserRemoteConfig><url>{url}</url></hudson.plugins.git.UserRemoteConfig></userRemoteConfigs>
      <branches><hudson.plugins.git.BranchSpec><name>*/main</name></hudson.plugins.git.BranchSpec></branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="empty-list"/>
      <extensions/>
    </scm>
    <scriptPath>{SP}</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>'''


print('upstream-main', jk.create_or_update('/job/verify-local', 'upstream-main',
      job_xml('https://github.com/Tuchsanai/DevTools.git', 'Upstream main Jenkinsfile, SCM mode (read-only compatibility check)')))
print('local-jenkinsfile', jk.create_or_update('/job/verify-local', 'local-jenkinsfile',
      job_xml('file:///var/jenkins_home/verify-local-repo.git', 'Modified Jenkinsfile from a local bare repo (not pushed)')))
