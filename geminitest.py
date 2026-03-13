from google import genai

client = genai.Client(api_key="AIzaSyBJknF48jExfMlloEZTlMm0ogVJbyJv6zI")

text = "The diner was quiet. Frank wiped the counter slow."

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"Give me one editorial note on this text: {text}"
)
print(response.text)

genai.configure(api_key=api_key)
model="gemini-1.5-flash"

text = "The diner was quiet. Frank wiped the counter slow."

response = model.generate_content(f"Give me one editorial note on this text: {text}")
print(response.text)
