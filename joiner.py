from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.errors import MForbidden
from mautrix.util.config import BaseProxyConfig, ConfigUpdateHelper
from typing import Type, List
import re


class Config(BaseProxyConfig):
    def do_update(self, helper: ConfigUpdateHelper) -> None:
        helper.copy("allowed_users")
        helper.copy("joined_rooms")
        helper.copy("command_prefix")

    def add_joined_room(self, room_id: str) -> None:
        if "joined_rooms" not in self:
            self["joined_rooms"] = []
        if room_id not in self["joined_rooms"]:
            self["joined_rooms"].append(room_id)
            self.save()


class JoinerBot(Plugin):
    """A maubot plugin that joins Matrix channels and rooms for you."""
    
    @classmethod
    def get_config_class(cls) -> Type[BaseProxyConfig]:
        return Config

    async def start(self) -> None:
        self.config.load_and_update()
        self.log.info(f"JoinerBot started")
        
        # Rejoin previously joined rooms on startup
        if "joined_rooms" in self.config:
            for room_id in self.config["joined_rooms"]:
                try:
                    await self.client.join_room(room_id)
                    self.log.info(f"Rejoined room {room_id}")
                except Exception as e:
                    self.log.error(f"Failed to rejoin room {room_id}: {e}")

    @command.new("joiner", help="Manage channel joining")
    async def joiner(self, evt: MessageEvent) -> None:
        """Base command handler."""
        self.log.info(f"Received joiner command from {evt.sender} in room {evt.room_id}")
        try:
            await evt.reply("Use !joiner add, list, or remove to manage channels")
            self.log.info("Replied to joiner command")
        except Exception as e:
            self.log.error(f"Error replying to joiner command: {e}")

    @command.new("ping", help="Check if the bot is responding")
    async def ping(self, evt: MessageEvent) -> None:
        """Simple ping command to check if the bot is responding."""
        self.log.info(f"Received ping command from {evt.sender} in room {evt.room_id}")
        try:
            await evt.reply("Pong! I'm here and listening.")
            self.log.info("Replied to ping command")
        except Exception as e:
            self.log.error(f"Error replying to ping command: {e}")

    @joiner.subcommand("add", help="Join a channel or room")
    @command.argument("room_id", pass_raw=True, required=True)
    async def add_channel(self, evt: MessageEvent, room_id: str) -> None:
        """Join a channel or room."""
        self.log.info(f"Received joiner add command from {evt.sender} in room {evt.room_id} with room_id: {room_id}")
        
        # Check if user is allowed to use this command
        sender = evt.sender
        if "allowed_users" in self.config and sender not in self.config["allowed_users"]:
            self.log.warning(f"Unauthorized user {sender} attempted to use joiner add command")
            await evt.reply("You are not authorized to use this command.")
            return

        # Clean up the room ID
        room_id = room_id.strip()
        self.log.info(f"Cleaned room_id: {room_id}")
        
        # Handle different room ID formats
        if room_id.startswith("#"):
            # It's an alias like #roomname:server.org
            if ":" not in room_id:
                self.log.warning(f"Invalid room format: {room_id}")
                await evt.reply("Invalid room format. Use #roomname:server.org")
                return
        elif not room_id.startswith("!"):
            # Not a room ID or alias, try to interpret as an alias
            if ":" not in room_id:
                self.log.warning(f"Invalid room format: {room_id}")
                await evt.reply("Invalid room format. Use #roomname:server.org or !roomid:server.org")
                return
            room_id = f"#{room_id}"
            self.log.info(f"Converted to alias format: {room_id}")

        try:
            # Try to join the room
            self.log.info(f"Attempting to join room {room_id}")
            await evt.reply(f"Attempting to join {room_id}...")
            join_info = await self.client.join_room(room_id)
            self.log.info(f"Join successful, got join_info: {join_info}")
            
            # Save the joined room to config
            self.log.info(f"Adding room {join_info} to config")
            self.config.add_joined_room(join_info)
            
            self.log.info(f"Successfully joined room {room_id}")
            await evt.reply(f"Successfully joined {room_id}")
        except MForbidden as e:
            self.log.error(f"Failed to join room {room_id}: Permission denied. Error: {e}")
            await evt.reply(f"Failed to join room: Permission denied. Error: {e}")
        except Exception as e:
            self.log.error(f"Failed to join room {room_id}: {e}")
            await evt.reply(f"Failed to join room: {e}")

    @joiner.subcommand("list", help="List joined channels")
    async def list_channels(self, evt: MessageEvent) -> None:
        """List all joined channels."""
        self.log.info(f"Received joiner list command from {evt.sender} in room {evt.room_id}")
        
        if "joined_rooms" not in self.config or not self.config["joined_rooms"]:
            self.log.info("No joined rooms found in config")
            await evt.reply("No channels have been joined yet.")
            return
        
        rooms = self.config["joined_rooms"]
        self.log.info(f"Found {len(rooms)} joined rooms in config")
        
        response = "Joined channels:\n"
        for room in rooms:
            response += f"- {room}\n"
        
        self.log.info(f"Sending list of joined rooms to {evt.sender}")
        try:
            await evt.reply(response)
            self.log.info("Successfully sent list of joined rooms")
        except Exception as e:
            self.log.error(f"Error sending list of joined rooms: {e}")

    @joiner.subcommand("remove", help="Leave a channel or room")
    @command.argument("room_id", pass_raw=True, required=True)
    async def remove_channel(self, evt: MessageEvent, room_id: str) -> None:
        """Leave a channel or room."""
        self.log.info(f"Received joiner remove command from {evt.sender} in room {evt.room_id} with room_id: {room_id}")
        
        # Check if user is allowed to use this command
        sender = evt.sender
        if "allowed_users" in self.config and sender not in self.config["allowed_users"]:
            self.log.warning(f"Unauthorized user {sender} attempted to use joiner remove command")
            await evt.reply("You are not authorized to use this command.")
            return

        # Clean up the room ID
        room_id = room_id.strip()
        self.log.info(f"Cleaned room_id: {room_id}")
        
        if "joined_rooms" not in self.config or room_id not in self.config["joined_rooms"]:
            self.log.info(f"Bot is not in room {room_id}")
            await evt.reply(f"Bot is not in room {room_id}")
            return
        
        try:
            # Try to leave the room
            self.log.info(f"Attempting to leave room {room_id}")
            await self.client.leave_room(room_id)
            
            # Remove from config
            self.log.info(f"Removing room {room_id} from config")
            self.config["joined_rooms"].remove(room_id)
            self.config.save()
            
            self.log.info(f"Successfully left room {room_id}")
            await evt.reply(f"Successfully left {room_id}")
        except Exception as e:
            self.log.error(f"Failed to leave room {room_id}: {e}")
            await evt.reply(f"Failed to leave room: {e}")
