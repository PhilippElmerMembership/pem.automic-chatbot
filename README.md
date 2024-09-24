# Automic Chatbot

This is an example of a chatbot using GPT function calls to perform tasks on the Broadcom Automic Automation platform. This software is for educational purposes only and was developed for an AI presentation and workshop during the 5 years PEM conference 2024 in Vienna. PEM is an independant e-learning platform for Broadcom Automic Automation, available in English (https://pemautomic.com) and German (https://membership.philippelmer.com).

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
LLM = "gpt-4o-mini"
```

## Usage

Start main.py and enjoy chatting. Amend prompts/system_prompt.py if you want to control the bot character.