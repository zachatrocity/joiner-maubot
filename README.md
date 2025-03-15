# Joiner Bot

A [maubot](https://github.com/maubot/maubot) plugin that joins Matrix channels and rooms for you.

! *note* - This started as a POC to see if I could use maubot to join rooms from a beeper.com matrix account. While I couldn't get it to work, this worked on my self hosted matrix instance so I decided to share.

## Features

- Join Matrix channels and rooms with a simple command
- Automatically rejoin rooms on bot restart
- List all joined rooms
- Leave rooms when no longer needed
- Optional user authorization to restrict who can use the bot

## Commands

- `!joiner add #roomname:server.org` - Join a channel or room
- `!joiner list` - List all joined channels
- `!joiner remove #roomname:server.org` - Leave a channel or room
- `!ping` - Check if the bot is responding

## Installation

1. Build the plugin:
   ```bash
   mbc build
   ```
   This will create a `.mbp` file in the current directory.

2. Upload the `.mbp` file to your maubot instance.

3. Create a client for the bot if you don't have one already.

4. Create an instance of the plugin and assign it to your client.

## Configuration

The plugin has the following configuration options:

- `allowed_users`: A list of Matrix user IDs that are allowed to use the bot. If empty, all users can use the bot.
- `joined_rooms`: A list of rooms the bot has joined. This is managed automatically by the bot.
- `command_prefix`: The prefix used for commands. Default is "!".

Example configuration:

```yaml
# List of Matrix user IDs that are allowed to use this bot
# If empty, all users can use the bot
allowed_users:
- "@admin:example.com"
- "@moderator:example.com"

# List of rooms the bot has joined
# This will be populated automatically as the bot joins rooms
joined_rooms:
- "#general:example.com"
- "#support:example.com"

# Command prefix (default is !)
# You can change this if you want to use a different prefix
command_prefix: "!"
```

## Development

This repository includes Nix configuration for setting up a development environment. You can use either the flake-based approach or the traditional nix-shell approach.

### Using Nix Flakes (Recommended)

If you have Nix with flakes enabled, you can enter the development environment with:

```bash
nix develop
```

> **Note:** The development environment requires the olm package, which may be marked as insecure in Nixpkgs. The flake.nix file includes configuration to allow this insecure package. If you encounter issues, you may need to manually allow it with `--impure --allow-insecure=olm-3.2.16`.

### Using Traditional nix-shell

If you prefer the traditional approach or don't have flakes enabled, you can use:

```bash
nix-shell
```

Both approaches will set up a Python virtual environment with all the necessary dependencies installed.

### Building the Plugin

Once in the development environment, you can build the plugin with:

```bash
mbc build
```

### Testing the Plugin

To test the plugin, you'll need to:

1. Set up a maubot instance (see the [maubot documentation](https://docs.mau.fi/maubot/index.html))
2. Upload the built `.mbp` file to your maubot instance
3. Create a client for the bot if you don't have one already
4. Create an instance of the plugin and assign it to your client

## License

This project is licensed under the GNU General Public License v3.0 - see the LICENSE file for details.
