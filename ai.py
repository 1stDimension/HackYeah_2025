with open(".env") as f:
    api_key = f.read()

# Replace the `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` values
# with appropriate values for your project.

from google import genai

# client = genai.Client(vertexai=True, api_key=api_key)

# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents="Explain bubble sort to me.",
# )

# print(response.text)
# Example response:
# Bubble Sort is a simple sorting algorithm that repeatedly steps through the list

from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)