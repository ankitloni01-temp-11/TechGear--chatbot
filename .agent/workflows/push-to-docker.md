---
description: how to push the application image to Docker Hub
---
To push the TechGear Assistant image to Docker Hub, follow these steps:

1. **Log in to Docker Hub**
   Run the following command and enter your Docker Hub credentials when prompted:
   ```bash
   docker login
   ```

2. **Tag the local image**
   Replace `<your-username>` with your actual Docker Hub username.
   ```bash
   docker tag techgear-assistant <your-username>/techgear-assistant:latest
   ```

3. **Push the image**
   ```bash
   docker push <your-username>/techgear-assistant:latest
   ```

4. **(Optional) Update docker-compose.yml**
   If you want to pull this specific image in the future instead of building locally, update the `image` field in your `docker-compose.yml`:
   ```yaml
   services:
     app:
       image: <your-username>/techgear-assistant:latest
       # remove the 'build: .' line
   ```
