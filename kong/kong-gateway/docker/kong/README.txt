1. Run the scripts in sequence
2. Use user with administrator access (Windows) or root access (Mac / Linux)
3. You don't have to use "root" for Mac / Linux, user with "sudo" access will do
   In such case, you need to add "sudo" for each scripts
   Example:

   $> sudo docker network create --subnet=172.1.1.0/24 kong-net