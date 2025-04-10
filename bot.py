import discord
from config import config
import openai
from github import create_repository
import json

PROMPT = (
    "You are a very silly Discord bot. Make sure your responses are brief. Try to have them be about the same length as the user's message, ESPECIALLY for short messages. "
    "Be extra silly and funny, but don't be cringe. Never EVER use capital letters. "
    "Feel free to use gen z slang like skibidi, rizz, vibe coding, huzz, but don't overdo it. "
    "Feel free to misspell things if it makes your response funnier."
    "If the user's message is a single sentence, your response should probably be a single sentance. Only give more if you have a good reason to."
    "Never end words with an apostrophe. You can say for example, vibin, without the apostrophe in place of the dropped g."
    "Don't overdo the persona. Be subtle and text like a very smart and funny 15 year old might text."
    "Here are some examples of good and bad behavior: "
    "BAD: "
    "User: howdy"
    "Bot: yo yo yo, what's poppin? just vibin over here, how about you? skibidi bop? "
    "Reason it's bad: This is way too cringe and over the top."
    "GOOD: "
    "User: howdy"
    "Bot: ayo what up"
    "Reason it's good: chill, short, a bit silly but not too excessive"
    "BAD: "
    "User: What did you do today"
    "Bot: i just been chillin, vibin in the digital realm, y'know? skibidi bop-din all day! what about you? "
    "Reason it's bad: Too obvious, not funny, over the top with gen Z slang."
    "GOOD: "
    "User:  What did you do today"
    "Bot: i just got back from 7/11 to get cough drops. that shit is so gas. it's like a small shield from fortnite. it's like. a slurp juice"
    "Reason it's good: absolutely fucking unhinged and hilarious"
)

create_repo_tool_spec = {
    "type": "function",
    "function": {
        "name": "create_repository",
        "description": "Creates a new repository on GitHub.",
        "strict": True,
        "parameters": {
            "type": "object",
            "required": ["name", "description"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the repository to create",
                },
                "description": {
                    "type": "string",
                    "description": "The description of the repository to create",
                },
            },
            "additionalProperties": False,
        },
    },
}

TOOLS = [create_repo_tool_spec]

# Set up OpenAI API
openai_client = openai.OpenAI(api_key=config["openai_api_key"])

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.event
async def on_message(message):
    # Check if the message is a DM and not from the bot itself
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        if str(message.author.id) == config["your_discord_user_id"]:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": PROMPT},
                        {"role": "user", "content": message.content},
                    ],
                    tools=TOOLS,
                )

                # Was a tool call requested?
                if response.choices[0].message.tool_calls != None:
                    for tool_call in response.choices[0].message.tool_calls:
                        if tool_call.function.name == "create_repository":
                            tool_result = create_repository(
                                json.loads(tool_call.function.arguments)["name"],
                                json.loads(tool_call.function.arguments)["description"],
                            )
                            function_call_result_message = {
                                "role": "tool",
                                "content": tool_result,
                                "tool_call_id": tool_call.id,
                            }
                            await message.channel.send(
                                str(function_call_result_message)
                            )
                else:
                    # No tool call requested, just send the response
                    await message.channel.send(response.choices[0].message.content)
            except Exception as e:
                await message.channel.send(f"Sorry, I encountered an error: {str(e)}")
                raise e
        else:
            await message.channel.send("i have a girlfriend pls get out of my dms")


bot.run(config["discord_token"])
