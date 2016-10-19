#!/usr/bin/env python3

import argparse
import discord
import asyncio

class commands():
	async def test(client, message, args):
		await client.send_message(message.channel, "Tested!")

	async def testedit(client, message, args):
		sleep_time = 5
		if len(args) > 0:
			try:	sleep_time = int(args[0])
			except:	pass
		mid = await client.send_message(message.channel, "Editing this message in {} seconds...".format(sleep_time))
		await asyncio.sleep(sleep_time)
		await client.edit_message(mid, "Edited!")

class TransportLayerBot(discord.Client):
	async def on_ready(self):
		print("Logged in as {}, ID {}.".format(self.user.name, self.user.id))

	async def on_message(self, message):
		if not message.author == self.user.id:
			if message.content[0] == '!':
				command, *args = message.content[1:].split()
				try:
					clientCommand = getattr(commands, command)
					try:
						await clientCommand(self, message, args)
					except Exception as e:
						await self.send_message(message.channel, "Something broke:\n```{}```".format(e))
				except AttributeError:
					pass	# Not a command.

def main():
	parser = argparse.ArgumentParser(description="TransportLayerBot for Discord")
	parser.add_argument("-t", "--token", type=str, metavar="TOKEN", dest="TOKEN", help="bot user application token", action="store", required=True)
	SETTINGS = vars(parser.parse_args())

	try:
		print("Starting TransportLayerBot with Discord version {}...".format(discord.__version__))

		client = TransportLayerBot()
		client.run(SETTINGS["TOKEN"])
	finally:
		print("Stopping...")
		client.logout()


if __name__ == "__main__":
	main()
