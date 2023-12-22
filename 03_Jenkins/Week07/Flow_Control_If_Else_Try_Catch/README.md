# Flow Control (Scripted)

<b>if..else</b>

```
pipeline {
    agent any
    environment{
        fname = "KAMAL"
    }
    stages {
        stage('one') {
            steps{
                script{
                    if (env.fname == 'KAMAL') {
                        echo 'HELLO KAMAL'
                    }
                    else{
                        echo 'I do not know you!'
                    }
                }
            }
            
        }
    }
}
```

<b>try...catch</b>

```
pipeline {
    agent any
    environment{
        fname = "KAMAL"
    }
    stages {
        stage('one') {
            steps{
                script{
                    try{
                        sh 'hello'
                    }
                    catch{
                        echo 'Error occured!!!!'
                    }
                }
            }
            
        }
    }
}
```

<p align="center">
<a href="https://www.youtube.com/c/xtremeexcel?sub_confirmation=1"><img src="/images/subscribe.gif" width="30%" height="30%"></a>
</p>
