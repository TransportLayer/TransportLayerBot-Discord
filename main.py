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

import argparse
import discord
import asyncio

class Commands():
	@staticmethod
	async def license(client, message, args):
		await client.send_message(message.channel, "I'm licensed under the GNU Affero General Public License.\nFor details, visit: https://www.gnu.org/licenses/agpl.html")

	@staticmethod
	async def source(client, message, args):
		await client.send_message(message.channel, "Get my source code here: https://github.com/TransportLayer/TransportLayerBot-Discord")

	@staticmethod
	async def test(client, message, args):
		await client.send_message(message.channel, "Tested!")

	@staticmethod
	async def testedit(client, message, args):
		sleep_time = 5
		if len(args) > 0:
			try:	sleep_time = int(args[0])
			except:	pass
		mid = await client.send_message(message.channel, "Editing this message in {} seconds...".format(sleep_time))
		await asyncio.sleep(sleep_time)
		await client.edit_message(mid, "Edited!")

commands = {
	"license": Commands.license,
	"source": Commands.source,
	"test": Commands.test,
	"testedit": Commands.testedit
}

class TransportLayerBot(discord.Client):
	async def on_ready(self):
		print("Logged in as {}, ID {}.".format(self.user.name, self.user.id))

	async def on_message(self, message):
		if not message.author == self.user.id:
			if message.content.startswith('!'):
				command, *args = message.content[1:].split()
				if command in commands:
					try:
						await commands[command](self, message, args)
					except Exception as e:
						await self.send_message(message.channel, "Something broke:\n```{}```".format(e))

def main():
	parser = argparse.ArgumentParser(description="TransportLayerBot for Discord")
	parser.add_argument("-t", "--token", type=str, metavar="TOKEN", dest="TOKEN", help="bot user application token", action="store", required=True)
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
		print("Starting TransportLayerBot with Discord version {}...".format(discord.__version__))

		client = TransportLayerBot()
		client.run(SETTINGS["TOKEN"])
	finally:
		print("Stopping...")
		client.logout()


if __name__ == "__main__":
	main()
