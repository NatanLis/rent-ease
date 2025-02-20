# Rent-Ease

Rent-Ease is a modern platform designed to simplify the process of managing and searching for rental properties. This project features a FastAPI backend paired with a Nuxt.js frontend, providing a robust and scalable solution for rental management. Please note that Rent-Ease is a mock application developed as a final project for university.

---

## Project Description

Rent-Ease leverages two main technologies:

- **Backend:** Built with [FastAPI](https://fastapi.tiangolo.com/), the API is lightweight, high-performance, and ideal for building modern web applications.
- **Frontend:** Powered by [Nuxt.js](https://nuxtjs.org/), the client application delivers a smooth, reactive user interface.

This project uses Mamba (a fast Conda alternative) for Python package management and Node.js (with Yarn) for managing the Nuxt.js frontend.

---

## Environment Setup

### Mac users

In order to use some of the scripts in the project, you need to install **newer** version of bash. to do that, follow these steps:

1. install new bash `brew install bash`
2. add new bash to searched paths `sudo sh -c 'echo /opt/homebrew/bin/bash >> /etc/shells'`
3. `chsh -s /opt/homebrew/bin`

### Python Environment with Mamba

To setup the environment, first you'll need to install [mamba](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html) (please note that in order to install mamba you need to download and install **miniforge** as stated in the documentation - you need to download it from [github repo](https://github.com/conda-forge/miniforge?tab=readme-ov-file#download) also mentioned in the docs) - a package manager for Python with capabilities to create virtual environments.

1. **Install Mamba:**
   - Follow the [Mamba documentation](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html) for installation instructions.
   - **Note:** Mamba requires [Miniforge](https://github.com/conda-forge/miniforge#download) to be installed.

2. **Create the Environment:**
   From the root of the project, run:

   ```bash
   mamba env create -f environment.yml
   ```

3. **Activate the Environment:**

   ```bash
   conda activate rent-ease
   ```

4. **Updating the Environment:**
   To update your environment when the `environment.yml` file changes, run:

   ```bash
   ./scripts/update
   ```

   or directly with:

   ```bash
   mamba env update -f environment.yml --prune
   ```

### Node.js and Nuxt Setup

1. **Install Node.js:**
   We recommend using [nvm](https://github.com/nvm-sh/nvm) to manage Node.js versions. Alternatively, you can install Node.js directly.

   - **macOS (using Homebrew):**

     ```bash
     brew install node
     ```

   - **Ubuntu:**

     ```bash
     curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
     sudo apt-get install -y nodejs
     ```

2. **Install Yarn:**
   Yarn is used as the package manager for the client application:

   ```bash
   npm install -g yarn
   ```

3. **Install Client Dependencies:**
   Navigate to the `client` directory and install dependencies:

   ```bash
   cd client
   yarn install
   ```

---

## Scripts and Commands

All helper scripts are located in the `scripts` folder. They streamline various development tasks:

### setup_env

Sets up the entire development environment:

- Creates the Python environment from `environment.yml`.
- Installs Node.js dependencies for the Nuxt client.
  
**Usage:**

```bash
./scripts/setup_env
```

### update

Updates both the Python environment and the Node.js client dependencies:

- Uses Mamba to update the environment (`mamba env update -f environment.yml --prune`).
- Runs `yarn install` in the client folder.

**Usage:**

```bash
./scripts/update
```

### run_dev

Runs both the FastAPI backend and Nuxt.js frontend concurrently using Honcho. The backend is served on port 8000 and the client on its default port.

**Usage:**

```bash
./scripts/run_dev
```

### lint

Runs pre-commit hooks to ensure code quality:

```bash
./scripts/lint
```

Alternatively, run:

```bash
pre-commit run --all-files
```

For the client (not supported right now):

```bash
cd client && yarn lint
```

---

## Development

### Running the Application Locally

To start both the backend and frontend for development, simply run:

```bash
./scripts/run_dev
```

This command launches:

- **FastAPI Backend:** Located in the `app` directory, served via `uvicorn`.
- **Nuxt.js Frontend:** Located in the `client` directory, running the Nuxt development server.

---

## Additional Information

- **FastAPI Backend:**  
  The FastAPI application resides in the `app` directory (main file: `app/main.py`).

- **Nuxt Frontend:**  
  The Nuxt.js client is located in the `client` directory. The main configuration is in `client/nuxt.config.js`.

- **Environment Variables:**  
  Make sure to set the following as needed:
  - `NODE_ENV` (e.g., `development` or `production`)
  - `ENV` (e.g., `dev`, `beta`, or `prod`)
  - `LANDING_ONLY` (set as `"True"` or `"False"`)

- **Favicons:**  
  Based on the `ENV` variable, ensure that the corresponding favicon file is available in your static/public directory:
  - `dev`: `/favicon-dev.ico`
  - `beta`: `/favicon-beta.ico`
  - `prod`: `/favicon.ico`
