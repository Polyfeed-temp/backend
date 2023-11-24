
from openai import OpenAI
apikey= "YOUR_API_KEY"
client = OpenAI(api_key=apikey)

def chat_completion(prompt):
    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].text

def explain_further(content):
    prompt = "Explain the following content in dot points:\n\n" + content + "\n\nExplaination:"
    return chat_completion(prompt)
