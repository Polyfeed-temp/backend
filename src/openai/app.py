import os

from openai import OpenAI

apikey = "api key"


def question(role, content):
    client = OpenAI(api_key=apikey)

    if len(content) >= 18000:
        print("Message is too long! Consider reducing the size of the message!")
        # this is an error to be printed out
    else:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": role, "content": content}
                # role: system. content: "Compose a poem that explains the concept of recursion in programming."
            ]
        )
        # print(completion.choices[0].message)
        return completion.choices[0].message
