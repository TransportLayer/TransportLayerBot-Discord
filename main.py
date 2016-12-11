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
from random import randint

def safe_string(dangerous_string):
	return dangerous_string.replace('\n', '\\n').replace('\r', '\\r').replace('\033[', '[CSI]').replace('\033', '[ESC]')

def setup_logger(level_string, log_file):
	numeric_level = getattr(logging, level_string.upper(), None)
	if not isinstance(numeric_level, int):
		raise Value("Invalid log level: {}".format(level_string))

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

	async def ask(self, client, source, no_prefix):
		if time() - self.session["last_message"] >= 5:
			self.session["last_message"] = time()
			if not no_prefix:
				source.content = source.content[len(client.user.id) + 4:]
			response = self.session["bot"].ask(source.content)
			await asyncio.sleep(randint(int(len(source.content) / 30), int(len(source.content) / 15)))

			await client.send_typing(source.channel)
			await asyncio.sleep(len(response) / 15)
			if self.session["name"]:
				response = "`{}`: {}".format(self.session["name"])
			await send_message(client, source, response)
		else:
			await send_message(client, source, "You're typing a bit too quickly for me! Try again in a few seconds.")

active_clevers = []

class TransportLayerBot(discord.Client):
	async def on_ready(self):
		logging.info("Logged in as {}, ID {}.".format(self.user.name, self.user.id))

	async def on_message(self, message):
		if not message.author.bot:
			await receive_message(message)

			if message.content.startswith('!'):
				command, *args = message.content[1:].split()
				if command in commands:
					try:
						await commands[command](self, message, args)
					except Exception as e:
						await send_warn(self, message, "!{} {}\n{}".format(command, args, e))

			elif message.content.startswith("<@{}>".format(self.user.id)) or message.channel.is_private:
				for clever in active_clevers:
					if message.channel == clever.session["channel"]:
						await clever.ask(self, message, message.channel.is_private)

def main():
	parser = argparse.ArgumentParser(description="TransportLayerBot for Discord")
	parser.add_argument("-t", "--token", type=str, metavar="TOKEN", dest="TOKEN", help="bot user application token", action="store", required=True)
	parser.add_argument("-l", "--log", type=str, metavar="LEVEL", dest="LOG_LEVEL", help="log level", action="store", default="INFO")
	parser.add_argument("-o", "--output", type=str, metavar="FILE", dest="LOG_FILE", help="file to write logs to", action="store", default="TransportLayerBot.log")
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

		logging.info("Starting TransportLayerBot with Discord version {}.".format(discord.__version__))

		client = TransportLayerBot()
		client.run(SETTINGS["TOKEN"])
	finally:
		logging.info("Stopping.")
		client.logout()

if __name__ == "__main__":
	main()
