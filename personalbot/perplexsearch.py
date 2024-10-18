from openai import OpenAI
from decouple import config

API_KEY = config('PERPLEX_API')

messages = [
    {
        "role" : "system",
        "content" : (
            "You are an helpful assistant"
        ),
    },
    {
        "role" : "user",
        "content" : (
            "what is perplexity"
        ),
    },
]

client = OpenAI(api_key=API_KEY, base_url="https://api.perplexity.ai")

response_stream = client.chat.completions.create(
    model="llama-3.1-sonar-small-128k-online",
    messages=messages,
    stream=True
)
for response in response_stream:

    print(response)
