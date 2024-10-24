ARG PYTHON_VERSION=3.10

# Step 1: Use an official Python runtime as a parent image
FROM python:${PYTHON_VERSION}-slim

# Step 2: Set the working directory in the container
WORKDIR /usr/src/app

# Step 3: Copy the requirements file into the container
COPY requirements.txt ./

# Step 5: Copy the requirements-dev file into the container
COPY requirements-dev.txt ./

# Step 6: Install any dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Step 7: Install build-essential. Will be needed to compile the node binaries.
RUN apt update && apt install -y build-essential

# Step 8: Copy the current directory contents into the container
COPY . .

# Step 9: Specify the command to run the application
ENTRYPOINT ["python", "-m", "multiversx_sdk_cli.cli"]