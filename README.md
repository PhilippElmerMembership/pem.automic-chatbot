# Automic Chatbot

This is an example on how an Automic chatbot could be implemented.

## Installation

Clone repository, create python virtual environment and install the dependencies.

```bash
git clone https://github.com/PhilippElmerMembership/pem.automic-chatbot.git
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Configuration

You need to provide an OpenAI API key to make use of the ChatCompletion API. It doesn't cost much, but it's necessary.

https://openai.com/api/

```plain
OPENAI_API_KEY="secret"
AUTOMIC_ENDPOINT = "https://[host]/ae/api/v1/[client]"
AUTOMIC_USERNAME = "automic-username"
AUTOMIC_PASSWORD = "automic-password"
LLM = "gpt-4-turbo"
```

## Usage

necessary.