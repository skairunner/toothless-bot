# Toothless

A Discord bot framework, written in Python and supporting plugins as plain Python modules. The biggest feature is subcommand routing, similar to Django's path routing.

Currently in development and unstable.

## Installing
Clone the repo and run:
```
$ pipenv install
```

## Running
Set your bot token as an envvar `BOTTOKEN`, then do:
```
$ pipenv run python start_bot.py
```

## Configuration
Configuration is done by config.py

# Plugins
Here's a brief description of the plugins that ship with Toothless by default.

## fakenitro
Reacts to messages that contain :emojiname: with the appropriate emoji.

## hello
A hello world script.

## timers
Unfinished. Contains /remindme features and /sprint features (similar to Pomodoro).

## utils
Server management utilities. Contains role management and mod statements.
