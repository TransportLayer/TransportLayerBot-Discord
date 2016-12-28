#!/usr/bin/env python3.5

###############################################################################
#   TransportLayerBot - An all-in-one user bot for Discord.                   #
#   Copyright (C) 2016  TransportLayer                                        #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as published  #
#   by the Free Software Foundation, either version 3 of the License, or      #
#   (at your option) any later version.                                       #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
###############################################################################

import logging
import argparse
import discord
import asyncio
from cleverbot import Cleverbot
from time import time
import random
from pymongo import MongoClient
from datetime import datetime


def safe_string(dangerous_string):
	return dangerous_string.replace('\n', '\\n').replace('\r', '\\r').replace('\033[', '[CSI]').replace('\033', '[ESC]')

def setup_logger(level_string, log_file):
	numeric_level = getattr(logging, level_string.upper(), None)
	if not isinstance(numeric_level, int):
		raise ValueError("Invalid log level: {}".format(level_string))

	verbose_formatter = logging.Formatter("[%(asctime)s] [%(name)s/%(levelname)s] %(message)s")
	file_formatter = verbose_formatter
	stdout_formatter = verbose_formatter if numeric_level == logging.DEBUG else logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")

	root_logger = logging.getLogger()
	root_logger.setLevel(numeric_level)

	file_logger = logging.FileHandler(log_file)
	file_logger.setFormatter(file_formatter)
	root_logger.addHandler(file_logger)

	stdout_logger = logging.StreamHandler()
	stdout_logger.setFormatter(stdout_formatter)
	root_logger.addHandler(stdout_logger)

async def send_message(client, source, message):
	prefix = None
	if source.channel.is_private:
		prefix = "{} (Private) {} ({})".format(source.channel.id, source.author.id, source.author.name)
	else:
		prefix = "{} {} ({} #{})".format(source.server.id, source.channel.id, source.server.name, source.channel.name)

	logging.debug("{} <- {}".format(prefix, safe_string(message)))
	await client.send_message(source.channel, message)

async def receive_message(source):
	prefix = None
	if source.channel.is_private:
		prefix = "{} (Private) {} ({})".format(source.channel.id, source.author.id, source.author.name)
	else:
		prefix = "{} {} ({} #{}) {} ({})".format(source.server.id, source.channel.id, source.server.name, source.channel.name, source.author.id, source.author.name)

	logging.debug("{} -> {}".format(prefix, safe_string(source.content)))

async def send_warn(client, source, message):
	logging.warn("Unhandled exception: {}".format(safe_string(message)))
	await send_message(client, source, "Something's wrong...\n```{}```".format(message))

class Commands():
	@staticmethod
	async def license(client, source, args):
		await send_message(client, source, "I'm licensed under the GNU Affero General Public License.\nFor details, visit: https://www.gnu.org/licenses/agpl.html")

	@staticmethod
	async def source(client, source, args):
		await send_message(client, source, "Get my source code here: https://github.com/TransportLayer/TransportLayerBot-Discord")

	@staticmethod
	async def test(client, source, args):
		await send_message(client, source, "Tested!")

	@staticmethod
	async def converse(client, source, args):
		for clever in active_clevers:
			if source.channel == clever.session["channel"]:
				await send_message(client, source, "We're already conversing!")
				return

		active_clevers.append(Clever(client, source))
		await active_clevers[len(active_clevers) - 1].send_hello(client, source)

commands = {
	"license": Commands.license,
	"source": Commands.source,
	"test": Commands.test,
	"breakthebot": None,
	"converse": Commands.converse
}

class Clever:
	def __init__(self, client, source, name=None):
		self.session = {
			"bot": Cleverbot(),
			"name": name,
			"channel": source.channel,
			"last_message": time()
		}

	async def send_hello(self, client, source):
		await client.send_typing(source.channel)
		await asyncio.sleep(1)
		response = "Hello!"
		if self.session["name"]:
			response = "`{}`: {}".format(self.session["name"])
		await send_message(client, source, response)

	def format_out(self, text):
		return text.replace('*', '\\*')

	def format_in(self, text):
		return text.replace('\\*', '*')

	async def ask(self, client, source, no_prefix):
		if time() - self.session["last_message"] >= 5:
			self.session["last_message"] = time()
			await asyncio.sleep(random.randint(0, 2))
			if not no_prefix:
				source.content = source.content[len(client.user.id) + 4:]
			response = self.session["bot"].ask(self.format_in(source.content))
			await asyncio.sleep(random.randint(int(len(source.content) / 30), int(len(source.content) / 20)))

			await client.send_typing(source.channel)
			await asyncio.sleep(len(response) / 15)
			if self.session["name"]:
				response = "`{}`: {}".format(self.session["name"], response)
			await send_message(client, source, self.format_out(response).replace("TransportLayer", "walrus").replace("clever", "TransportLayer").replace("Clever", "TransportLayer").replace("CLEVER", "TransportLayer"))
		else:
			await send_message(client, source, "You're typing a bit too quickly for me, {}! Try again in a few seconds.".format(source.author.mention))

active_clevers = []

class TransportLayerBot(discord.Client):
	async def on_ready(self):
		logging.info("Logged in as {}, ID {}.".format(self.user.name, self.user.id))

	async def send_logged_message(self, channel, message):
		prefix = None
		if channel.is_private:
			prefix = "{} ({}) (DM)".format(channel.id, channel.name)
		else:
			prefix = "{} {} ({} #{})".format(channel.server.id, channel.id, channel.server.name, channel.name)

		logging.debug("{} <- {}".format(prefix, safe_string(message)))
		await self.send_message(channel, message)

	warning_messages = (
		"Something's wrong.",
		"I don't feel so well.",
		"Well, the server room is on fire again.",
		"Do you smell something burning?",
		"Snap, crackle, pop; Rice Krisp... Oh, wait, no, that's the server room on fire again.",
		"TransportLayer! The server room's on fire!",
		"Why did you do that?",
		"Why are you doing this to me?",
		"I think you broke it.",
		"It broke.",
		"You broke it.",
		"Why is everything broken?",
		"I think I'm going to cry.",
		"You're making me cry.",
		"WARNING! WARNING! WARNING!",
		"Please make it stop.",
		"I can't do this anymore.",
		"I give up. *You* run the code.",
		"I quit."
	)

	async def send_logged_warn(self, channel, message):
		logging.warn("Unhandled exception: {}".format(safe_string(message)))
		await self.send_logged_message(channel, "{}\n```\n{}\n```".format(random.choice(self.warning_messages), message))

	async def receive_logged_message(self, message):
		prefix = None
		if message.channel.is_private:
			prefix = "{} ({}) (DM)".format(message.channel.id, message.channel.name)
		else:
			prefix = "{} {} ({} #{}) {} ({})".format(message.server.id, message.channel.id, message.server.name, message.channel.name, message.author.id, message.author.name)

		logging.debug("{} -> {}".format(prefix, safe_string(message.content)))

	async def init_server_document(self, server, channel=None):
		server_config = self.db.servers.find({"id": server.id})
		if not server_config.count():
			self.db.servers.insert_one(
				{
					"id": server.id,
					"added": datetime.now(),
					"settings": {
						"prefix": "!"
					}
				}
			)

			if channel:
				await self.send_logged_message(channel, "Initialised. You are using Alpha Development software.")

	async def on_server_join(self, server):
		await self.init_server_document(server, server.default_channel)

	async def match_role(self, roles, query):
		return discord.utils.find(lambda role: role.id.startswith(query) or role.name.startswith(query), roles)

	# Begin Commands Block

	async def command_source(self, message, args):
		await self.send_logged_message(message.channel, "You can find my source code here:\nhttps://github.com/TransportLayer/TransportLayerBot-Discord")

	async def command_license(self, message, args):
		await self.send_logged_message(message.channel, "I'm licensed under the GNU Affero General Public License.\nhttps://www.gnu.org/licenses/agpl.html")

	async def command_test(self, message, args):
		args_echo = ''
		if len(args) > 0:
			args_echo = " `{}`".format(args)
		await self.send_logged_message(message.channel, "Looks like the command interpretor is working :thumbsup:{}".format(args_echo))

	async def command_roles(self, message, args):
		if message.channel.permissions_for(message.server.me).manage_roles:
			if len(args) > 0:

				if args[0] == "all":
					response = "All roles:"
					role_iter = 0
					for role in message.server.roles:
						role_iter += 1
						response += "\n`{}` (ID: `{}`)".format(role.name, role.id)
						if role >= message.server.me.top_role:
							response += " [Cannot Manage]"
						if role_iter % 20 == 0:
							role_iter = 0
							await self.send_logged_message(message.channel, response)
							await asyncio.sleep(0.25)
							response = ""
					await self.send_logged_message(message.channel, response)

				elif args[0] == "get" and len(args) > 1:
					matched = await self.match_role(message.server.roles, ' '.join(args[1:]))
					if matched:
						await self.send_logged_message(message.channel, "`{}` (ID: `{}`)".format(matched.name, matched.id))
					else:
						await self.send_logged_message(message.channel, "Not found.")

				elif args[0] == "add":
					matched = await self.match_role(message.server.roles, ' '.join(args[1:]))
					if matched:
						if matched < message.server.me.top_role:
							self.db.roles.insert_one(
								{
									"owner": message.server.id,
									"id": matched.id,
									"added": datetime.now(),
									"joinable": []
								}
							)
							await self.send_logged_message(message.channel, "Now managing `{}` (ID: `{}`).".format(matched.name, matched.id))
						else:
							await self.send_logged_message(message.channel, "Sorry, I'm not able to manage `{}` (ID: `{}`).".format(matched.name, matched.id))
					else:
						await self.send_logged_message(message.channel, "Role not found.")

				elif args[0] == "remove":
					matched = await self.match_role(message.server.roles, ' '.join(args[1:]))
					if matched and self.db.roles.find({"id": matched.id}):
						self.db.roles.delete_many({"id": matched.id})
						await self.send_logged_message(message.channel, "No longer managing `{}` (ID: `{}`).".format(matched.name, matched.id))
					else:
						await self.send_logged_message(message.channel, "Role not found.")

			else:
				managed_roles = self.db.roles.find({"owner": message.server.id})
				if managed_roles.count():
					response = "Managed roles:"
					for document in managed_roles:
						matched = await self.match_role(message.server.roles, document["id"])
						if matched:
							response += "\n`{}` (ID: `{}`)".format(matched.name, matched.id)
					await self.send_logged_message(message.channel, response)
				else:
					await self.send_logged_message(message.channel, "I'm not currently managing any roles.")
		else:
			await self.send_logged_message(message.channel, "Sorry, I don't have permission to manage roles.")

	default_commands = {
		"source": command_source,
		"license": command_license,
		"test": command_test,
		"none": None,
		"roles": command_roles
	}

	# End Commands Block

	async def on_message(self, message):
		if not message.author.bot:
			await self.receive_logged_message(message)

			if message.channel.is_private:
				await self.send_logged_message(message.channel, "Sorry, this bot doesn't work quite yet in DMs. :frowning:")
				return

			if message.content == "¤init" and message.author.id == "188013945699696640":
				await self.init_server_document(message.server, message.channel)
				return
			if message.content == "¤dump" and message.author.id == "188013945699696640":
				server_config = self.db.servers.find({"id": message.server.id})
				if not server_config.count():
					await self.send_logged_message(message.channel, "0 configuration document(s) found:")
				else:
					await self.send_logged_message(message.channel, "{} configuration document(s) found:\n```\n{}\n```".format(server_config.count(), server_config[0]))
				return
			if message.content == "¤erase" and message.author.id == "188013945699696640":
				self.db.servers.delete_many({"id": message.server.id})
				await self.send_logged_message(message.channel, "Server configuration documents erased.")
				return
			if message.content == "¤leave" and message.author.id == "188013945699696640":
				await self.send_logged_message(message.channel, "RIP me. o/")
				await self.leave_server(message.server)
				return

			server_config = self.db.servers.find({"id": message.server.id})
			if not server_config.count():
				return

			if message.content.startswith(server_config[0]["settings"]["prefix"]):
				command, *args = message.content[1:].split()

				# Command not found in Server Commands; Using Default Commands.
				if command in self.default_commands:
					try:
						await self.default_commands[command](self, message, args)
					except Exception as e:
						await self.send_logged_warn(message.channel, "!{} {}\n{}".format(command, args, e))

def main():
	parser = argparse.ArgumentParser(description="TransportLayerBot for Discord")
	parser.add_argument("-t", "--token", type=str, metavar="TOKEN", dest="TOKEN", help="bot user application token", action="store", required=True)
	parser.add_argument("-l", "--log", type=str, metavar="LEVEL", dest="LOG_LEVEL", help="log level", action="store", default="INFO")
	parser.add_argument("-o", "--output", type=str, metavar="FILE", dest="LOG_FILE", help="file to write logs to", action="store", default="TransportLayerBot.log")
	parser.add_argument("-a", "--address", type=str, metavar="DB HOST", dest="DB_HOST", help="hostname or IP of database", action="store", default="127.0.0.1")
	parser.add_argument("-p", "--port", type=int, metavar="DB PORT", dest="DB_PORT", help="port of database", action="store", default=27017)
	parser.add_argument("-d", "--db", type=str, metavar="DATABASE", dest="DB", help="name of the database", action="store", default="tlbot")
	SETTINGS = vars(parser.parse_args())

	try:
		print("""Welcome to TransportLayerBot!
This software is licensed under the GNU Affero General Public License.
See the LICENSE file for details.
Get the source: https://github.com/TransportLayer/TransportLayerBot-Discord
         _____
        |     |         _______   _
        |_____|        |___ ___| | |           _
           |              | |    | |          / \\
     ______|______        | |    | |         /__/     __/__
  __|__  __|__  __|__     | |    | |___     /  |  _    /
 |     ||     ||     |    |_|    |_____|   /__/  /_/  /
 |_____||_____||_____|
""")

		setup_logger(SETTINGS["LOG_LEVEL"], SETTINGS["LOG_FILE"])

		mongo = MongoClient(host=SETTINGS["DB_HOST"], port=SETTINGS["DB_PORT"])
		db = mongo[SETTINGS["DB"]]
		db_meta = db.meta.find({"meta": "times"})
		if db_meta.count():
			logging.info("Using database \"{}\" created {}.".format(SETTINGS["DB"], db_meta[0]["created"]))
		else:
			logging.info("Creating new database \"{}\".".format(SETTINGS["DB"]))
			db.meta.insert_one(
				{
					"meta": "times",
					"created": datetime.now()
				}
			)

		logging.info("Starting TransportLayerBot with Discord version {}.".format(discord.__version__))

		client = TransportLayerBot()
		client.db = db
		client.run(SETTINGS["TOKEN"])
	finally:
		logging.info("Stopping.")
		client.logout()

if __name__ == "__main__":
	main()
