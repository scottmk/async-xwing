Feature: Player slash commands
    As a player
    I want to use player slash commands to read and modify my player state

    Scenario: Player Stats
        Given the bot is running and ready
        And I am a player "TestPlayer" with two ships "1" and "2"
        When I execute the "/player stats" command for "TestPlayer"
        Then the bot should post a header message for "TestPlayer"
        And the bot should create a thread named "TestPlayer's ships"
        And the bot should print "lukeskywalker" and "jekporkins" stat blocks to the thread
