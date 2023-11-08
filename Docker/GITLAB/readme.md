Installing GitLab with Docker involves pulling the official GitLab Docker image and running a container with the appropriate configuration. Here’s a step-by-step guide to installing GitLab using Docker:

1. **Install Docker**: Make sure Docker is installed on your system. If not, you can download it from the official Docker website and follow the installation instructions for your operating system.

2. **Pull GitLab Docker Image**: You can pull the official GitLab Docker image from Docker Hub by running the following command:

   ```sh
   docker pull gitlab/gitlab-ce:latest
   ```

3. **Run GitLab Container**: Once the image is pulled, you can run a container from that image. You’ll need to specify various parameters such as the hostname, external URL, and any volumes you want to persist data:

   ```sh
   docker run --detach \
     --hostname gitlab.example.com \
     --publish 443:443 --publish 80:80 --publish 22:22 \
     --name gitlab \
     --restart always \
     --volume /srv/gitlab/config:/etc/gitlab \
     --volume /srv/gitlab/logs:/var/log/gitlab \
     --volume /srv/gitlab/data:/var/opt/gitlab \
     gitlab/gitlab-ce:latest
   ```

   This command will start a new container named `gitlab`, with GitLab running inside it. It binds the container’s ports 443, 80, and 22 to the same ports on the host machine. It also sets up three volumes to ensure data persistence for configuration, logs, and data.

   Replace `gitlab.example.com` with the hostname you want to use for your GitLab instance.

4. **Access GitLab**: After the container starts, you should be able to access GitLab by going to `http://gitlab.example.com` or `http://localhost` from your web browser. It might take a few minutes for GitLab to start up completely.

5. **Initial Configuration**: Upon first accessing GitLab, you will be prompted to set up an admin password. After setting the password, you can log in with the username `root` and the password you just created.

6. **Configure GitLab (Optional)**: If you need to make configuration changes to GitLab, you can edit the `gitlab.rb` file inside the `/srv/gitlab/config` directory on the host machine and then reconfigure the GitLab container by running:

   ```sh
   docker exec -it gitlab gitlab-ctl reconfigure
   ```

This guide assumes you have basic familiarity with Docker commands and concepts like images, containers, volumes, and port mapping. Remember to replace placeholder values with actual values relevant to your setup. Also, ensure that the ports GitLab uses are not being used by another service on the host machine.