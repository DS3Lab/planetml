---
sidebar_position: 1
---

# Welcome!

The Together Open Models API provides researchers with access to open foundation models. Currently, we are providing:

* Batch inference on language models (e.g., OPT, BLOOM, etc.).
* Batch inference on image models (e.g., stable diffusion).
* Training / fine-tuning access to open language models (coming soon).

In a nutshell:

You give us a jsonl file where each line is a request (format very similar to the OpenAI API for language models).
We give you back a jsonl file with the results of each request.
Language models that are supported:

* GPT-J (6B)
* GPT-NeoX (20B)
* OPT (66B)
* OPT (175B)
* T5 (11B)
* T0++ (11B)
* UL2 (20B)
* YaLM (100B)
* BLOOM (176B)
* GLM (130B)

Image models that are supported:

* DALL-E mini
* DALL-E mega
* Stable diffusion

In more detail:

* Create a jsonl file with a set of requests that you want. Look at this example.
* Run this validator script to check the format.
* Join the #open-models-api channel in the Together discord channel and submit a request to the TOMA bot with the following information:

  * A brief 1-2 paragraph description of your project.
  * A URL to a jsonl file with your requests (you can host it anywhere).
  * An indication of whether you will allow us to make all the requests and responses public. This is optional, but public workloads will be prioritized.

```
/toma <url to jsonl file>
```

* We will send you back an URL of your response jsonl file.
* When you publish your work, please mention that you used the Together Computer for doing inference or training on the various models.
* Very soon, we have a proper website to make this more ergonomic.