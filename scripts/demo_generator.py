from src.script_generator.generator import generate_script


topic = "Why do we replay conversations in our heads?"

print("Generating script...\n")

script = generate_script(topic)

print("TITLE:", script.title)
print("\nTOPIC:", script.topic)
print("\nHOOK:", script.hook)
print("\nFULL SCRIPT:", script.full_script)
print("\nTAKEAWAY:", script.takeaway)