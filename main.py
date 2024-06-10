from Immortal import Immortal
import os
import json
import discord
import aiohttp

# Hugging Face model API endpoint
API_URL = 'https://api-inference.huggingface.co/models/SwordMasterO/'

class MyClient(discord.Client):
    def __init__(self, model_name):
        # Adding intents to prevent intents error
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.api_endpoint = API_URL + model_name
        huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
        self.request_headers = {
            'Authorization': f'Bearer {huggingface_token}'
        }

    async def query(self, payload):
        """
        Make request to the Hugging Face model API
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_endpoint, headers=self.request_headers, json=payload) as response:
                print("Response Status Code:", response.status)
                response_text = await response.text()
                print("Response Content:", response_text)  # Debug print

                if response_text:
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError as json_err:
                        print(f"JSON decode error: {json_err}")
                        return {'error': f"JSON decode error: {json_err}"}
                else:
                    print("Empty response received.")
                    return {'error': 'Empty response received from the API'}

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.query({'inputs': 'Hello!'})

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        payload = {'inputs': message.content}

        async with message.channel.typing():
            response = await self.query(payload)

        if isinstance(response, list) and len(response) > 0:
            bot_response = response[0].get('generated_text', 'Hmm... something is not right.')
        else:
            bot_response = 'Hmm... something is not right.'

        if 'error' in response:
            bot_response = f'`Error: {response["error"]}`'

        await message.channel.send(bot_response)

def main():
    client = MyClient('DialoGPT-medium-Hermione')
    Immortal()
    client.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    main()
