from godalle import get_typesense_client
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

available_models_mapping = {
    "Image: stable_diffusion": "stable_diffusion",
    "Text: GPT-6B": 'gpt-j-6b',
    "Text: GPT-Neox": 'gpt-neox-20b',
    "Text: T0PP": 't0pp',
    "Text: T5": 't5-11b',
    "Text: UL2": 'ul2',
}

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
        if 'choices' in raw_output['result']:
            return raw_output['result']['choices'][0]['text']
        elif 'result' in raw_output['result'][0]:
            return raw_output['result'][0]['result']['choices'][0]['text']
        else:
            return "something went wrong"

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
    embed_job_info.add_field(
            name=f"Model", value=f"{model}", inline=False)
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
async def search(
    ctx: discord.ApplicationContext,
    prompt: discord.Option(str, description="Input your prompts", name="prompts"),
):
    ts_client = get_typesense_client()
    await ctx.defer()
    search_parameters = {
        'q': prompt,
        'query_by': 'title',
    }
    records = ts_client.collections['records'].documents.search(search_parameters)
    embed_job_info = discord.Embed(
            title=f"A search query created!", description="Keyword: " + prompt, color=0x00ff00)
    embed_job_info.add_field(name=f"Prompts", value=f"{prompt}", inline=False)
    for idx, record in enumerate(records['hits']):
        rs = record['document']
        rs['img_name'] = rs['img_name'].replace(".bmp", ".jpg")
        if not rs['img_name'].startswith("https://"):
            rs['img_name'] = os.path.join(rs['category'], rs['img_name'])
            rs['img_name'] = "http://52.36.141.204/imgs/" + rs['img_name']
        records['hits'][idx]['document'] = rs
    embed_job_info.set_image(url=records['hits'][0]['document']['img_name'])
    embed_job_info.add_field(name=f"Feedback", value="""
        👍 => Good   👎 => Bad   🤣 => Funny
        🚫 => Inappropriate   😱 => Scary
    """, inline=False)
    view = FeedbackView()
    msg = await ctx.send_followup(embed=embed_job_info, view=view)
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')
    await msg.add_reaction('🤣')
    await msg.add_reaction('🚫')
    await msg.add_reaction('😱')

@bot.slash_command()
async def toma(
    ctx: discord.ApplicationContext,
    prompt: discord.Option(str, description="Input your prompts",
                           name="prompts"),
    model: discord.Option(str, description="Choose your model",
                          choices=[
                              "Image: stable_diffusion",
                              "Text: gpt-j-6b",
                              "Text: gpt-neox-20b",
                              "Text: t0pp",
                              "Text: t5",
                              "Text: ul2"
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
        if model.startswith("Image"):
            mode = 'Image Generation'
        elif model.startswith("Text"):
            mode = 'Text Generation'
        else:
            raise Exception("Invalid model")
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
            elif model =='Text: gpt-neox-20b':
                model = 'gpt-neox-20b'
            elif model == 'Text: t0pp':
                model = 't0pp'
            elif model == 'Text: t5':
                model = 't5-11b'
            elif model == 'Text: ul2':
                model = 'ul2'
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
        embed_job_info.add_field(
            name=f"Model", value=f"{model}", inline=False)

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
