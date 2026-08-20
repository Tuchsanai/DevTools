import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.security.HudsonPrivateSecurityRealm
import jenkins.model.Jenkins

def instance = Jenkins.get()
def realm = new HudsonPrivateSecurityRealm(false)
realm.createAccount('admin', 'admin2569')
instance.setSecurityRealm(realm)

def authorization = new FullControlOnceLoggedInAuthorizationStrategy()
authorization.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(authorization)
instance.save()
