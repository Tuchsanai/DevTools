# GCP GPU Request Lab

## Overview

This lab provides step-by-step instructions for requesting GPUs on Google Cloud Platform (GCP). The lab uses 11 images stored in the `img` folder to visually guide you through the process.

## Prerequisites

Before you begin, ensure that you have the following:

- A Google Cloud Platform (GCP) account.
- The `gcloud` command-line tool installed and configured.
- Access to a GCP project with billing enabled.
- The `img` folder containing 11 images relevant to this lab.

## Lab Steps

### 1. Set Up Your GCP Environment

1. Open a terminal or command prompt.
2. Authenticate with your GCP account:

    ```bash
    gcloud auth login
    ```

3. Set the active project:

    ```bash
    gcloud config set project [YOUR_PROJECT_ID]
    ```

### 2. Request a GPU

1. Navigate to the Compute Engine section in the GCP Console.
2. Click on **Create Instance**.
3. Use the following settings to request a GPU:

    - **Name**: Choose a unique name for your instance.
    - **Region/Zone**: Select a region and zone where GPUs are available.
    - **Machine Type**: Choose a machine type that supports GPUs.
    - **GPU Type**: Select the GPU type and quantity you need.

4. Review the cost estimate and click **Create**.

5. Use the images in the `img` folder for visual guidance on each step.

### 3. Accessing the Instance

1. Once the instance is created, go to the VM Instances page in the Compute Engine section.
2. Click **SSH** to access your instance.
3. Verify the GPU availability:

    ```bash
    nvidia-smi
    ```

### 4. Clean Up

After completing your lab, remember to delete the resources to avoid unnecessary charges:

```bash
gcloud compute instances delete [INSTANCE_NAME]
