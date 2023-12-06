
from openai import OpenAI

apikey =  "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"


def question(role, content):
    client = OpenAI(api_key=apikey)

    if len(content) >= 18000:
        print("Message is too long! Consider reducing the size of the message!")
        # this is an error to be printed out
    else:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": role, "content": content}
                # role: system. content: "Compose a poem that explains the concept of recursion in programming."
            ]
        )
        # print(completion.choices[0].message)
        return completion.choices[0].message

# apikey= "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"
# client = OpenAI(api_key=apikey)

def chat_completion(prompt):
    # response = client.chat.completions.create(
    #   model="gpt-3.5-turbo",
    #   messages=[{"role": "system", "content": prompt}]
    # )
    # return response.choices[0].text
    return question("system", prompt)

def explain_further(content:str):
    prompt = "Explain the following content in dot points:\n\n" + content + "\n\nExplaination:"
    return chat_completion(prompt)
