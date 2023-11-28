from app import question
# apikey= "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"
# client = OpenAI(api_key=apikey)

def chat_completion(prompt):
    # response = client.chat.completions.create(
    #   model="gpt-3.5-turbo",
    #   messages=[{"role": "system", "content": prompt}]
    # )
    # return response.choices[0].text
    return question("system", prompt)

def explain_further(content):
    prompt = "Explain the following content in dot points:\n\n" + content + "\n\nExplaination:"
    return chat_completion(prompt)
