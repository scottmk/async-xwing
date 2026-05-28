# async-xwing
Discord bot for asynchronous implementation of the FFG TMG X-wing

- [Setup a Test Server](#setup-a-test-server)
- [Setup a Test Application and Test Bot](#setup-a-test-application-and-test-bot)
  - [Run Locally](#run-locally)
    - [Prerequisites](#prerequisites)

## Setup a Test Server

1. Enable developer mode on your Discord client, if you have not already
1. Create a new Discord Server
1. Setup a Test Bot - [follow these instructions](https://discordpy.readthedocs.io/en/stable/discord.html)
1. Invite your Test Bot to your server

## Setup a Test Application and Test Bot

Follow the instructions [here](https://discordpy.readthedocs.io/en/stable/discord.html)

### Run Locally

#### Prerequisites
1. Install python 3.14
   - If you have homebrew installed, you can do so with the following command:
       ```zsh
       brew install python@3.14
       ```
1. Clone the github repo
1. Create a python venv
   - If using VSCode, bring up the command palette with `Cmd + Shift + P` and execute `Python: Create Environment...`
      - Make sure you select python3.14
   - If using command line, navigate to the repo directory and run the following commands:
       ```zsh
       python3 venv bot-env
       source bot-env/bin/activate
       ```
1. Install discord.py:
    ```zsh
    pip install -U discord.py
    ```
1. Add the bot to your server (see above instructions)
1. Create a `.env` file and create an entry for `TOKEN`, set to your bot's token
1. Execute the `hello_world` test bot:
    ```zsh
    python hello_world.py
    ```
1. Send the test message "$hello" to your test server. You should get a response from the bot. Inspect `hello_world.log` to make sure logging works correctly.
