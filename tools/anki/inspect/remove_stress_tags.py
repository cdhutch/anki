import os
import re

pattern = re.compile(r'^- stress:(verified|unverified)\n', re.MULTILINE)

for root, dirs, files in os.walk('domains/ua/anki/notes'):
    for file in files:
        if file.endswith('.md'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = pattern.sub('', content)
            
            if modified != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(modified)
                print(f"Processed: {filepath}")

print("Done")