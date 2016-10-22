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
from cleverbot import Cleverbot
import random

clever_session = {
	"started": False,
	"channel": None,
	"bot_a": ["Bot A", None],
	"bot_b": ["Bot B", None],
	"last_response": ''
}

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

	@staticmethod
	async def play(client, message, args):
		await client.change_presence(game=discord.Game(name=' '.join(args), url="https://github.com/TransportLayer/TransportLayerBot-Discord", type=0), status=None, afk=False)
		await client.send_message(message.channel, "Now playing {}!".format(' '.join(args)))

	@staticmethod
	async def stopplaying(client, message, args):
		await client.change_presence(game=discord.Game(name=None, url=None, type=None), status=None, afk=False)
		await client.send_message(message.channel, "Stopped playing!")

	@staticmethod
	async def pretendtotype(client, message, args):
		await client.send_message(message.channel, "Pretending to type!")
		await client.send_typing(message.channel)

	#@staticmethod
	#async def initvoice(client, message, args):
	#	await discord.opus.load_opus("libopus.so.1")

	@staticmethod
	async def checkvoice(client, message, args):
		if discord.opus.is_loaded():
			await client.send_message(message.channel, "Voice libraries loaded!")
		else:
			await client.send_message(message.channel, "Not ready!")

	#@staticmethod
	#async def testvoice(client, message, args):
	#	vchannel = discord.utils.get(message.server.channels, name='Music 1', type=discord.ChannelType.voice)
	#	vclient = await client.join_voice_channel(vchannel)
	#	vplayer = vclient.create_ffmpeg_player("/home/nsg/Downloads/Far_Away_Sting.mp3")
	#	vplayer.volume = 0.25
	#	#vplayer = await vclient.create_ytdl_player("https://www.youtube.com/watch?v=_FQwhJn1Dls", options="-af volume=0.25")
	#	vplayer.start()

	@staticmethod
	async def playyt(client, message, args):
		vchannel = discord.utils.get(message.server.channels, name='Music 1', type=discord.ChannelType.voice)
		vclient = await client.join_voice_channel(vchannel)
		try:
			vplayer = await vclient.create_ytdl_player(args[0])
			if vplayer.duration <= 360:
				await client.change_presence(game=discord.Game(name="{}...".format(vplayer.title[:37]), url=vplayer.url, type=1), status=None, afk=False)
				await client.send_message(message.channel, "Now playing {}".format(vplayer.title))
				vplayer.volume = 0.25
				vplayer.start()
				await asyncio.sleep(vplayer.duration + 1)
				await client.change_presence(game=discord.Game(name=None, url=None, type=None), status=None, afk=False)
			else:
				await client.send_message(message.channel, "Refusing to play (video too long).".format(vplayer.title))
		except Exception as e:
			await client.send_message(message.channel, "Cannot play:\n```{}```".format(e))
		await vclient.disconnect()

	@staticmethod
	async def cleverstart(client, message, args):
		if not clever_session["started"] and len(args) >= 2:
			clever_session["started"] = True
			random.seed()
			clever_session["channel"] = message.channel
			clever_session["bot_a"][0] = args[0]
			clever_session["bot_a"][1] = Cleverbot()
			clever_session["bot_b"][0] = args[1]
			clever_session["bot_b"][1] = Cleverbot()
			await client.send_message(clever_session["channel"], "`Session started!`")
			if len(args) > 2:
				clever_session["last_response"] = ' '.join(args[2:])
				await client.send_message(clever_session["channel"], "`{}`: {}".format(clever_session["bot_a"][0], clever_session["last_response"]))
			while clever_session["started"]:
				clever_session["last_response"] = clever_session["bot_b"][1].ask(clever_session["last_response"])
				await client.send_typing(clever_session["channel"])
				await asyncio.sleep(random.randint(1, 3))
				await client.send_message(clever_session["channel"], "`{}`: {}".format(clever_session["bot_b"][0], clever_session["last_response"]))
				await asyncio.sleep(random.randint(3, 10))
				await client.send_typing(clever_session["channel"])
				await asyncio.sleep(random.randint(1, 3))
				clever_session["last_response"] = clever_session["bot_a"][1].ask(clever_session["last_response"])
				await client.send_message(clever_session["channel"], "`{}`: {}".format(clever_session["bot_a"][0], clever_session["last_response"]))
				await asyncio.sleep(random.randint(3, 10))

	@staticmethod
	async def cleverstop(client, message, args):
		if clever_session["started"]:
			clever_session["started"] = False
			await client.send_message(clever_session["channel"], "`Session killed :(`")
			clever_session["channel"] = None
			clever_session["bot_a"] = ["Bot A", None]
			clever_session["bot_b"] = ["Bot B", None]
			clever_session["last_response"] = ''

commands = {
	"license": Commands.license,
	"source": Commands.source,
	"test": Commands.test,
	"testedit": Commands.testedit,
	"play": Commands.play,
	"stopplaying": Commands.stopplaying,
	"pretendtotype": Commands.pretendtotype,
	#"initvoice": Commands.initvoice,
	"checkvoice": Commands.checkvoice,
	#"testvoice": Commands.testvoice,
	"playyt": Commands.playyt,
	"cleverstart": Commands.cleverstart,
	"cleverstop": Commands.cleverstop
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
