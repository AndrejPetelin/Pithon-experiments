from google import genai

client = genai.Client(api_key="AIzaSyDLdOn1UmuzaFYBrKSJcTkzxYXxdcoS4Q0")

text = "The diner was quiet. Frank wiped the counter slow."

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=f"Give me one editorial note on this text: {text}"
)
print(response.text)

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash-latest")

text = "The diner was quiet. Frank wiped the counter slow."

response = model.generate_content(f"Give me one editorial note on this text: {text}")
print(response.text)
