import os
import discord
import torch
from transformers import AutoTokenizer, AutoModelWithLMHead

# Define constants for model and API
MODEL_NAME = "SwordMasterO/DialoGPT-medium-Hermione"

# Initialize tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelWithLMHead.from_pretrained(MODEL_NAME)

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author.id == self.user.id:
            return

        # Encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(message.content + tokenizer.eos_token, return_tensors='pt')

        # Append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if 'chat_history_ids' in globals() else new_user_input_ids

        # Generate a response while limiting the total chat history to 1000 tokens
        chat_history_ids = model.generate(
            bot_input_ids, max_length=200,
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=3,
            do_sample=True,
            top_k=100,
            top_p=0.7,
            temperature=0.8
        )

        # Decode the response and send it back to the Discord channel
        response_text = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        await message.channel.send(response_text)

def main():
    # Instantiate the bot client
    client = MyClient()
    # Run the bot with the token from the environment variable
    client.run(os.getenv('DISCORD_TOKEN'))

if __name__ == '__main__':
    main()
