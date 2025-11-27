import google.generativeai as genai

genai.configure(api_key="AIzaSyA7OTmiUR_aIsUDZrNUjEMp_7AHX3HBDsE")

print("List of available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)