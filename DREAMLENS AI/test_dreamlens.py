from app_advanced import dreamlens

print("Extracted context:")
print(dreamlens.extract_context("I was chased by a big elephant and fell into the water, woke up sad"))

print("\nCalling interpret_dream (LLM call may fail if no local server is running):\n")
try:
    result = dreamlens.interpret_dream("I was chased by a big elephant and fell into the water, woke up sad")
    print(result[:1500])
except Exception as e:
    print('Error while calling interpret_dream:', e)
