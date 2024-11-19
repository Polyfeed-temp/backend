# 1. enter comments
# 2. filter and leave unique comments only
# 3. generate summaries based on these comments, repeat for several times, until we have a few summaries
# 4. Using these summaries, to genberate key themes
# This file is for future extension usage

from app import question
import os
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4o-mini")

os.environ.get("OPENAI_API_KEY")

with open('/Users/aaronzheng/PycharmProjects/ChatGPTTest/comments') as f:
    comments = f.read()
    comments = comments.replace("\n", "")
    comments = comments.replace("\t", "")

token_count = len(encoding.encode(comments))

# Define the maximum token limit per minute
max_text_per_minute = 18000
# 75 words is roughly 100 tokens

# Split the text into chunks based on the token limit
text_chunks = []
start_idx = 0

while start_idx < len(comments):
    end_idx = start_idx + max_text_per_minute
    if end_idx > len(comments):
        end_idx = len(comments)

    chunk = comments[start_idx:end_idx]
    text_chunks.append(chunk)
    start_idx = end_idx

# Send chunks to the API
for chunk in text_chunks:
    # response = question("user", "Summarise these comments into a few key themes:" + chunk)
    response = question("user", "Summarise 10 common issues from these feedbacks" + chunk)
    # identify ten common strength
    # identify ten common weaknesses
    print(response)



# What has been achieved:
# 1. There is no problem if the student would like to check out a summarised version of their comments - an individual summary.
# Each summary takes about 15 seconds to 40 seconds to generate. Most of them takes about 20 seconds
# 2. It might be available to ask ChatGPT to summarise text, however, it might be wise to remove all "\n", "\t" beforehand.
# 3. It might also be doable to ask ChatGPT to conduct the second iteration of summarisation.

# issues:
# 1. hard to estimate how many tokens is reasonable - 75 words is about 100 tokens. This might be able to resolve.
# 2. super long running time. It takes roughly  minutes to complete 110000 words summarisation, and this is only the first stage.
# It is better if this is run before the results are released/stuents have access to the results, otherwise the function will simply not work
# due to massive runtime.
# This was an error after 10 min running:
# openai.BadRequestError: Error code: 400 - {'error': {'message': "This model's maximum context length is 4097 tokens. However, your messages resulted in 4105 tokens. Please reduce the length of the messages.", 'type': 'invalid_request_error', 'param': 'messages', 'code': 'context_length_exceeded'}}
# 3. Over the first successful trying (18000 letters, ), it appears that the key themes that ChatGPT generated during the first iteration of summarisation
# is too subjective, meaning it was summarised based on the comments that was given to every student, instead of a few very general points.
# 4. There is a chance that ChatGPT might summarise something that no one understands. For example,"d doesn't die. Should only drop runes if the player dies."
# Human verification is required before details are published.
# 5.