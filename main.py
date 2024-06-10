import os
import discord
from Immortal import Immortal
from huggingface_hub import InferenceClient

# Initialize the Hugging Face Inference Client with an access token
hf_access_token = os.getenv('HUGGINGFACE_TOKEN')
client = InferenceClient(token=hf_access_token)

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self, intents):
        super().__init__(intents=intents)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        async with message.channel.typing():
            try:
                # Make a request to the Hugging Face model for chat completion
                response = client.chat_completion(
                    messages=[{"role": "user", "content": message.content}],
                    model="SwordMasterO/DialoGPT-medium-Hermione"
                )
                print(f"Response: {response}")  # Debug print to inspect the response structure

                # Extract the generated response from the Hugging Face model
                if isinstance(response, dict) and 'choices' in response and len(response['choices']) > 0:
                    bot_response = response['choices'][0].get('message', {}).get('content', 'Hmm... something is not right.')
                else:
                    bot_response = 'Hmm... something is not right.'

            except Exception as e:
                print(f"Request error occurred: {e}")
                bot_response = 'Hmm... something went wrong.'

        # Send the model's response to the Discord channel
        await message.channel.send(bot_response)

def main():
    # Instantiate the bot client
    client = MyClient(intents=intents)
    # Run the bot with the token from the environment variable
    Immortal()
    client.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    main()
