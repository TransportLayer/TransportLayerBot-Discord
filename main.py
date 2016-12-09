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
	logging.debug("{} {} ({} #{}) <- {}".format(source.server.id, source.channel.id, source.server.name, source.channel.name, safe_string(message)))
	await client.send_message(source.channel, message)

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

commands = {
	"license": Commands.license,
	"source": Commands.source,
	"test": Commands.test,
	"breakthebot": None
}

class TransportLayerBot(discord.Client):
	async def on_ready(self):
		logging.info("Logged in as {}, ID {}.".format(self.user.name, self.user.id))

	async def on_message(self, message):
		if not message.author.bot:
			if message.content.startswith('!'):
				command, *args = message.content[1:].split()
				if command in commands:
					try:
						await commands[command](self, message, args)
					except Exception as e:
						await send_warn(self, message, "!{} {}\n{}".format(command, args, e))

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
