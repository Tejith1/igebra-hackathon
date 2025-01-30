# igebra-hackathon

A Flask-based chat application that includes user authentication, chat functionality, and the ability to generate PDFs from chat responses using the Groq AI API.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

This project is a web-based chat application built with Flask. It includes user authentication, chat functionality, and the ability to generate PDFs from chat responses using the Groq AI API. Users can register, log in, and chat with the AI assistant. The assistant can provide detailed research and analysis on user-provided topics, and users can generate PDFs containing the chat responses.

## Features

- User registration and login with hashed passwords
- Chat functionality with AI-generated responses
- PDF generation from chat responses
- MongoDB for user data storage
- Secure user authentication with Flask-Login and Flask-Bcrypt

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/Tejith1/your-repo-name.git
    ```
2. Navigate to the project directory:
    ```sh
    cd your-repo-name
    ```
3. Create a virtual environment:
    ```sh
    python -m venv venv
    ```
4. Activate the virtual environment:
    ```sh
    # On Windows
    venv\Scripts\activate

    # On macOS/Linux
    source venv/bin/activate
    ```
5. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Set the Groq API key as an environment variable:
    ```sh
    export GROQ_API_KEY="your-groq-api-key"
    ```
2. Run the application:
    ```sh
    python app.py
    ```
3. Open your web browser and navigate to `http://localhost:5000` to access the application.

## Configuration

Ensure you set the following environment variables for the project to run:

- `GROQ_API_KEY`: Your Groq AI API key

Example of setting environment variables:
```sh
export GROQ_API_KEY="your-groq-api-key"
