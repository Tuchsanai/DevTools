
### Objective `CMD` and `ENTRYPOINT`

The goal of this lab is to understand:
- How `CMD` and `ENTRYPOINT` instructions define a container's default behavior.
- The difference in behavior when using them separately and together.
- How to override the default behavior defined by these instructions.

### Prerequisites

- Docker installed on your machine.

### Lab Setup



## create directory

   
    mkdir LAB0_Week11
    cd    LAB0_Week11
    

## git clone branch dev
    
    
   ```
    git clone -b dev https://github.com/Tuchsanai/DevTools.git
   ```
   
   ```   
    cd DevTools/02_Docker/Week11/00_LAB_CMD_Entrypoint/
   ```


1. **Create a Dockerfile for CMD**

   First, we'll create a simple Dockerfile that uses `CMD`.

   ```Dockerfile
   # Dockerfile-CMD
   FROM ubuntu
   CMD ["echo", "Hello from CMD!"]
   ```

   - Build the image by using Dockerfile = Dockerfile-CMD and tag it as `cmd-example`:
     ```
     docker build -t cmd-example -f Dockerfile-CMD .
     ```

   - Run the container without any arguments:
     ```
     docker run cmd-example
     ```

   - Run the container with arguments:
     ```
     docker run cmd-example echo "CMD with custom message"
     ```

   This demonstrates how `CMD` sets the default command and how it can be overridden by command-line arguments.

2. **Create a Dockerfile for ENTRYPOINT**

   Next, create a Dockerfile that uses `ENTRYPOINT`.

   ```Dockerfile
   # Dockerfile-ENTRYPOINT
   FROM ubuntu
   ENTRYPOINT ["echo", "Hello from ENTRYPOINT!"]
   ```

   - Build the image by using Dockerfile = Dockerfile-ENTRYPOINT and tag it as `entrypoint-example`:
     ```
     docker build -t entrypoint-example -f Dockerfile-ENTRYPOINT .
     ```

   - Run the container without any arguments:
     ```
     docker run entrypoint-example
     ```

   - Run the container with arguments:
     ```
     docker run entrypoint-example "ENTRYPOINT with custom message"
     ```

   This shows how `ENTRYPOINT` sets a fixed command (in this case, `echo`) and appends any command-line arguments to it.

3. **Combining CMD and ENTRYPOINT**

   Finally, let's combine `CMD` and `ENTRYPOINT` in a Dockerfile to see how they work together.

   ```Dockerfile
   # Dockerfile-CMD-ENTRYPOINT
   FROM ubuntu
   ENTRYPOINT ["echo"]
   CMD ["Hello from both CMD and ENTRYPOINT!"]
   ```

   - Build the image:
     ```
     docker build -t cmd-entrypoint-example -f Dockerfile-CMD-ENTRYPOINT .
     ```

   - Run the container without any arguments:
     ```
     docker run cmd-entrypoint-example
     ```

   - Run the container with arguments:
     ```
     docker run cmd-entrypoint-example "Custom message with both CMD and ENTRYPOINT"
     ```

   Here, `ENTRYPOINT` specifies the executable (`echo`), and `CMD` provides default arguments which can be overridden by command-line arguments when running the container.

### Conclusion

This lab demonstrates the fundamental differences and interactions between `CMD` and `ENTRYPOINT`:
- `CMD` specifies default commands and arguments that can be overridden.
- `ENTRYPOINT` specifies a fixed command (executable), with `CMD` providing default parameters that can be appended to or overridden by command-line arguments.
- Together, they offer flexibility in defining container runtime behavior, making Docker a powerful tool for deploying and managing applications in various environments.