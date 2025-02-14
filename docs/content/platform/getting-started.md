# Getting Started with AutoGPT: Self-Hosting Guide

This tutorial will walk you through the process of setting up AutoGPT locally on your machine.

<center><iframe width="560" height="315" src="https://www.youtube.com/embed/4Bycr6_YAMI?si=dXGhFeWrCK2UkKgj" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></center>

## Introduction

This guide will help you setup the server and builder for the project.

<!-- The video is listed in the root Readme.md of the repo -->

We also offer this in video format. You can check it out [here](https://github.com/Significant-Gravitas/AutoGPT?tab=readme-ov-file#how-to-setup-for-self-hosting).

!!! warning
    **DO NOT FOLLOW ANY OUTSIDE TUTORIALS AS THEY WILL LIKELY BE OUT OF DATE**

## Prerequisites

To setup the server, you need to have the following installed:

- [Node.js](https://nodejs.org/en/)
- [Docker](https://docs.docker.com/get-docker/)
- [Git](https://git-scm.com/downloads)

#### Checking if you have Node.js & NPM installed

We use Node.js to run our frontend application.

If you need assistance installing Node.js:
https://nodejs.org/en/download/

NPM is included with Node.js, but if you need assistance installing NPM:
https://docs.npmjs.com/downloading-and-installing-node-js-and-npm

You can check if you have Node.js & NPM installed by running the following command:

```bash
node -v
npm -v
```

Once you have Node.js installed, you can proceed to the next step.

#### Checking if you have Docker & Docker Compose installed

Docker containerizes applications, while Docker Compose orchestrates multi-container Docker applications.

If you need assistance installing docker:
https://docs.docker.com/desktop/

Docker-compose is included in Docker Desktop, but if you need assistance installing docker compose: 
https://docs.docker.com/compose/install/

You can check if you have Docker installed by running the following command:

```bash
docker -v
docker compose -v
```

Once you have Docker and Docker Compose installed, you can proceed to the next step.

### Cloning the Repository
The first step is cloning the AutoGPT repository to your computer.
To do this, open a terminal window in a folder on your computer and run:
```
git clone https://github.com/Significant-Gravitas/AutoGPT.git
```
If you get stuck, follow [this guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

Once that's complete you can close this terminal window.

### Running the backend services

To run the backend services, follow these steps:

* Within the repository, clone the submodules and navigate to the `autogpt_platform` directory:
  ```bash
   git submodule update --init --recursive --progress
   cd autogpt_platform
  ```
  This command will initialize and update the submodules in the repository. The `supabase` folder will be cloned to the root directory.

* Copy the `.env.example` file available in the `supabase/docker` directory to `.env` in `autogpt_platform`:
  ```
   cp supabase/docker/.env.example .env
  ```
  This command will copy the `.env.example` file to `.env` in the `supabase/docker` directory. You can modify the `.env` file to add your own environment variables.

* Run the backend services:
  ```
   docker compose up -d --build
  ```
  This command will start all the necessary backend services defined in the `docker-compose.combined.yml` file in detached mode.


### Running the frontend application

To run the frontend application, follow these steps:

* Navigate to `frontend` folder within the `autogpt_platform` directory:
  ```
   cd frontend
  ```

* Copy the `.env.example` file available in the `frontend` directory to `.env` in the same directory:
  ```
   cp .env.example .env
  ```
  You can modify the `.env` within this folder to add your own environment variables for the frontend application.

* Run the following command:
  ```
   npm install
   npm run dev
  ```
  This command will install the necessary dependencies and start the frontend application in development mode.

### Checking if the application is running

You can check if the server is running by visiting [http://localhost:3000](http://localhost:3000) in your browser.

**Notes:**
 
By default the application for different services run on the following ports: 

Frontend UI Server: 3000
Backend Websocket Server: 8001
Execution API Rest Server: 8006

#### Additional Notes

You may want to change your encryption key in the `.env` file in the `autogpt_platform/backend` directory.

To generate a new encryption key, run the following command in python:

```python
from cryptography.fernet import Fernet;Fernet.generate_key().decode()
```

Or run the following command in the `autogpt_platform/backend` directory:

```bash
poetry run cli gen-encrypt-key
```

Then, replace the existing key in the `autogpt_platform/backend/.env` file with the new one.
