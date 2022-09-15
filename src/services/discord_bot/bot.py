import discord
import requests
from time import sleep
from table2ascii import table2ascii
from discord.ui import InputText, Modal
import requests
from datetime import datetime
import os
# read the token from env var\
TOKEN = os.environ['TOMA_DISCORD_BOT_TOKEN']

endpoint = 'https://planetd.shift.ml'

def submit_job(prompt, model='stable_diffusion'):
    job = requests.post(endpoint + '/jobs', json={
        "type": "general",
        "payload": {
            "model": model,
            "num_returns": 1,
            "input": [
                prompt
            ]
        },
        "returned_payload": {},
        "status": "submitted",
        "source": "dalle",
        "processed_by": ""
    })
    job_id = job.json()['id']
    return job_id


def fetching_results(job_id):
    addr = None
    while True:
        res = requests.get(endpoint + '/job/' + job_id).json()
        if res['status'] == 'finished':
            addr = res['returned_payload']['filename']
            break
        sleep(5)
    raw_output = requests.get(addr).json()
    return raw_output['output']


bot = discord.Bot()


@bot.event
async def on_ready():
    # bot.add_view(FeedbackView())  # Registers a View for persistent listening
    print('ready')


@bot.slash_command()
async def draw(
    ctx: discord.ApplicationContext,
    prompt: discord.Option(str, description="Input your prompts", name="prompts"),
):
    print(prompt)
    await ctx.defer()
    model = 'stable_diffusion'
    job_id = submit_job(prompt, model=model)

    if job_id is None:
        await ctx.send_followup(f"Something went wrong")
        return

    embed_job_info = discord.Embed(
        title=f"Job Info {job_id}", description="Job ID: " + job_id, color=0x00ff00, url=f"https://toma.pages.dev/report/{job_id}")

    embed_job_info.add_field(name=f"Prompts", value=f"{prompt}", inline=False)

    embed_job_info.add_field(name=f"Feedback", value="""
        👍 => Good   👎 => Bad   🤣 => Funny
        🚫 => Inappropriate   😱 => Scary
    """, inline=False)

    embed_job_info.set_footer(text=f"# Generated with {model} by TOMA")
    await ctx.send_followup(embed=embed_job_info)
    results = fetching_results(job_id)
    for prompt in results:
        for img in prompt:
            await ctx.send_followup(img)

bot.run(TOKEN)
