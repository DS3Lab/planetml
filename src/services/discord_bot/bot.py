from views import FeedbackView
from stats_command import get_cluster_status, get_model_status
import discord
import requests
import os
import asyncio
import traceback

import sys
sys.path.append(".")

TOKEN = os.environ['TOMA_DISCORD_BOT_TOKEN']
endpoint = 'http://192.168.191.9:5005'
bot = discord.Bot()


async def submit_job(prompt, model='stable_diffusion', task='Image Generation', args=None):
    print(task)
    if task == 'Image Generation':
        data = {
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
        }
    elif task == 'Text Generation':
        data = {
            "type": "general",
            "payload": {
                "best_of": 1,
                "echo": False,
                "logprobs": 1,
                "max_tokens": args['max_tokens'],
                "model": model,
                "n": 1,
                "prompt": prompt,
                "request_type": "language-model-inference",
                "stop": ["\n"],
                "temperature": args['temperature'],
                "top_p": args['top_p'],
            },
            "returned_payload": {},
            "status": "submitted",
            "source": "dalle",
            "processed_by": ""
        }
    job = requests.post(endpoint + '/jobs', json=data)
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
    if 'output' in raw_output:
        return raw_output['output']
    else:
        return raw_output['result']['choices'][0]['text']


async def respond_image(ctx, job_id, prompt, model):
    results = await fetching_results(job_id)
    embed_job_info = discord.Embed(
        title=f"Job Results {job_id}", description="Results for Job " + job_id, color=0x00ff00, url=f"https://toma.pages.dev/report/{job_id}")
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


async def respond_text(ctx, job_id, prompt, model):
    results = await fetching_results(job_id)
    embed_job_info = discord.Embed(
        title=f"Job Results {job_id}", description="Results for Job " + job_id, color=0x00ff00, url=f"https://toma.pages.dev/report/{job_id}")
    embed_job_info.add_field(name=f"Prompts", value=f"{prompt}", inline=False)
    embed_job_info.add_field(name=f"Results", value=f"{results}", inline=False)
    embed_job_info.add_field(name=f"Feedback", value="""
        👍 => Good   👎 => Bad   🤣 => Funny
        🚫 => Inappropriate   😱 => Scary
    """, inline=False)

    embed_job_info.set_footer(text=f"# Generated with {model} by TOMA")
    view = FeedbackView()
    msg = await ctx.send_followup(embed=embed_job_info, view=view)
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')
    await msg.add_reaction('🤣')
    await msg.add_reaction('🚫')
    await msg.add_reaction('😱')


@bot.event
async def on_ready():
    bot.add_view(FeedbackView())  # Registers a View for persistent listening
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

        embed_job_info.add_field(
            name=f"Prompts", value=f"{prompt}", inline=False)

        await ctx.send_followup(embed=embed_job_info)
        asyncio.ensure_future(respond_image(ctx, job_id, prompt, model))
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
                         choices=['Image Generation', 'Text Generation'],
                         default="Image Generation"),
    model: discord.Option(str, description="Choose your model",
                          choices=[
                              "Image: stable_diffusion",
                              "Text: gpt-j-6b",
                          ],
                          default="Image: stable_diffusion"),
    max_tokens: discord.Option(int, min_value=1, max_value=1024, required=False, description="(Text Generation) max_tokens",default=140),
    temperature: discord.Option(float, min_value=0, max_value=1, required=False, description="(Text Generation) temperature", default=0),
    top_p: discord.Option(float, min_value=0, max_value=1, default=1,
                          required=False, description="(Text Generation) top_p")
):
    await ctx.defer()
    try:
        job_id = None
        if mode == "Image Generation":
            if model == 'Image: stable_diffusion':
                model = 'stable_diffusion'
            else:
                await ctx.send_followup(f"Error: Model {model} not found")
                return
            job_id = await submit_job(prompt, model=model, task=mode)

        elif mode == "Text Generation":
            if model == 'Text: gpt-j-6b':
                model = 'gpt-j-6b'
            else:
                await ctx.send_followup(f"Error: Model {model} not found")
                return
            args = {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
            
            job_id = await submit_job(
                prompt,
                model=model,
                task=mode,
                args=args
            )
            print(job_id)

        if job_id is None:
            await ctx.send_followup(f"Something went wrong")
            return

        embed_job_info = discord.Embed(
            title=f"Job Created: {job_id}", description="Job ID: " + job_id, color=0x00ff00, url=f"https://toma.pages.dev/report/{job_id}")

        embed_job_info.add_field(
            name=f"Prompts", value=f"{prompt}", inline=False)

        if mode == "Image Generation":
            await ctx.send_followup(embed=embed_job_info)
            asyncio.ensure_future(respond_image(ctx, job_id, prompt, model))

        elif mode == "Text Generation":
            await ctx.send_followup(embed=embed_job_info)
            asyncio.ensure_future(respond_text(
                ctx, job_id, prompt, model))

    except Exception as e:
        error = traceback.format_exc()
        await ctx.send_followup(f"sorry, something went wrong. \n\n ```{error}```")

if __name__ == "__main__":
    bot.run(TOKEN)
