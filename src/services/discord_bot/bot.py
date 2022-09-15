import discord
import requests
import requests
import os
import asyncio
import traceback

import sys
sys.path.append(".")
from stats_command import get_cluster_status, get_model_status
from views import FeedbackView

TOKEN = os.environ['TOMA_DISCORD_BOT_TOKEN']
endpoint = 'https://planetd.shift.ml'
bot = discord.Bot()

async def submit_job(prompt, model='stable_diffusion'):
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


async def fetching_results(job_id):
    addr = None
    while True:
        res = requests.get(endpoint + '/job/' + job_id).json()
        if res['status'] == 'finished':
            addr = res['returned_payload']['filename']
            break
        await asyncio.sleep(5)
    raw_output = requests.get(addr).json()
    return raw_output['output']


async def respond(ctx, job_id, prompt, model):
    results = await fetching_results(job_id)
    embed_job_info = discord.Embed(
            title=f"Job Results {job_id}", description="Results for Job" + job_id, color=0x00ff00, url=f"https://toma.pages.dev/report/{job_id}")
    embed_job_info.add_field(name=f"Prompts", value=f"{prompt}", inline=False)

    embed_job_info.add_field(name=f"Feedback", value="""
        👍 => Good   👎 => Bad   🤣 => Funny
        🚫 => Inappropriate   😱 => Scary
    """, inline=False)

    embed_job_info.set_footer(text=f"# Generated with {model} by TOMA")
    view = FeedbackView()
    for prompt in results:
        for img in prompt:
            embed_job_info.set_image(url=img)
            msg = await ctx.send_followup(embed=embed_job_info, view=view)

            await msg.add_reaction('👍')
            await msg.add_reaction('👎')
            await msg.add_reaction('🤣')
            await msg.add_reaction('🚫')
            await msg.add_reaction('😱')

@bot.event
async def on_ready():
    bot.add_view(FeedbackView()) # Registers a View for persistent listening
    print('ready')
    return

@bot.slash_command()
async def draw(
    ctx: discord.ApplicationContext,
    prompt: discord.Option(str, description="Input your prompts", name="prompts"),
):
    print(prompt)
    await ctx.defer()
    try:

        model = 'stable_diffusion'
        job_id = await submit_job(prompt, model=model)

        if job_id is None:
            await ctx.send_followup(f"Something went wrong")
            return

        embed_job_info = discord.Embed(
            title=f"Job Created: {job_id}", description="Job ID: " + job_id, color=0x00ff00, url=f"https://toma.pages.dev/report/{job_id}")

        embed_job_info.add_field(name=f"Prompts", value=f"{prompt}", inline=False)

        await ctx.send_followup(embed=embed_job_info)
        asyncio.ensure_future(respond(ctx, job_id, prompt, model))
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        await ctx.send_followup(f"sorry, something went wrong. \n\n ```{error}```")

@bot.slash_command()
async def together(
    ctx: discord.ApplicationContext,
    command: discord.Option(
        str,
        description="Get status of current resources and usage",
        choices=["cluster status", "model status"],
    ),
    *,
    args=""
):
    await ctx.defer()
    try:
        if command == "cluster status":
            responds = get_cluster_status(args)
            await ctx.send_followup(f"{responds}")
        elif command == "model status":
            responds = get_model_status(args)
            await ctx.send_followup(f"{responds}")
    except Exception:
        error = traceback.format_exc()
        print(error)
        await ctx.send_followup(f"sorry, something went wrong. \n\n ```{error}```")

@bot.slash_command()
async def toma(
    ctx: discord.ApplicationContext,
    prompt: discord.Option(str, description="Input your prompts", 
        name="prompts"),
    mode: discord.Option(str, description="Choose your mode",
        choices=['Image Generation'],
        default = "Image Geneartion"),
    model: discord.Option(str, description="Choose your model",
        choices=[
            "Image: stable_diffusion"
        ],
        default = "default"),
    max_tokens: discord.Option(int, min_value=1, max_value=1024, required=False, description="(Text Generation) max_tokens"),
    temperature: discord.Option(float, min_value=0, max_value=1, required=False, description="(Text Generation) temperature"),
    top_p: discord.Option(float, min_value=0, max_value=1, required=False, description="(Text Generation) top_p")
):
    await ctx.defer()
    try:
        print(prompt)
        model = 'stable_diffusion'
        job_id = await submit_job(prompt, model=model)

        if job_id is None:
            await ctx.send_followup(f"Something went wrong")
            return

        embed_job_info = discord.Embed(
            title=f"Job Created: {job_id}", description="Job ID: " + job_id, color=0x00ff00, url=f"https://toma.pages.dev/report/{job_id}")

        embed_job_info.add_field(name=f"Prompts", value=f"{prompt}", inline=False)

        await ctx.send_followup(embed=embed_job_info)
        asyncio.ensure_future(respond(ctx, job_id, prompt, model))
    except Exception as e:
        error = traceback.format_exc()
        print(error)
        await ctx.send_followup(f"sorry, something went wrong. \n\n ```{error}```")

if __name__=="__main__":
    bot.run(TOKEN)
