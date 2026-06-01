# async-xwing Development
Discord bot for asynchronous implementation of the FFG TMG X-wing

- [Getting Started](#getting-started)
    - [Setup a Test Server](#setup-a-test-server)
    - [Setup a Test Application and Test Bot](#setup-a-test-application-and-test-bot)
    - [Run Locally](#run-locally)
        - [Prerequisites](#prerequisites)
- [Working with game state](#working-with-game-state)
- [Running the main bot locally](#running-the-main-bot-locally)

## Getting Started

### Setup a Test Server

1. Enable developer mode on your Discord client, if you have not already
1. Create a new Discord Server
1. Setup a Test Bot - [follow these instructions](https://discordpy.readthedocs.io/en/stable/discord.html)
1. Invite your Test Bot to your server

### Setup a Test Application and Test Bot

Follow the instructions [here](https://discordpy.readthedocs.io/en/stable/discord.html)

#### Run Locally

##### Prerequisites
1. Install python 3.14
   - If you have homebrew installed, you can do so with the following command:
       ```zsh
       brew install python@3.14
       ```
1. Clone the github repo
1. Install dependencies:
    ```zsh
    uv sync
    ```
1. Add the bot to your server (see above instructions)
1. Create a `.env` file and create an entry for `TOKEN`, set to your bot's token
1. Execute the `hello_world` test bot:
    ```zsh
    uv run hello_world.py
    ```
1. Send the test message "$hello" to your test server. You should get a response from the bot. Inspect `hello_world.log` to make sure logging works correctly.

## Working with game state

In your `.env` file, under `TOKEN`, add the following:

```
GAME_STATE_PATH='data/gamestates'
GAME_NUMBER='1'
```

This will ensure you can properly read from and save to the game state.

## Running the main bot locally

1. Ensure you follow the steps above in [Getting Started](#getting-started)
1. Ensure your `.env` is properly setup by following the steps in [Working with game state](#working-with-game-state)
1. Execute
    ```zsh
    uv run main.py
    ```
1. Logs will be saved under `./xwing.log`
