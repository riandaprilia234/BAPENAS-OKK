import json
import re

transcript_path = 'C:/Users/LENOVO/.gemini/antigravity/brain/1194b7c8-a846-417a-8359-433c7fd417a3/.system_generated/logs/transcript_full.jsonl'
output_dir = 'c:/Users/LENOVO/Documents/BAPENAS 2026/QR-ABSEN/'

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            step = json.loads(line)
            if step.get('type') == 'TOOL_RESPONSE' and step.get('name') == 'view_file':
                content = step.get('content', '')
                if 'File Path: ' in content:
                    file_path = re.search(r'File Path: `file:///([^`]+)`', content)
                    if file_path:
                        path_str = file_path.group(1).replace('%20', ' ')
                        if 'QR-ABSEN' in path_str:
                            # Extract content between "1: <original_line>" format
                            lines = []
                            for c_line in content.split('\n'):
                                match = re.match(r'^\d+: (.*)', c_line)
                                if match:
                                    lines.append(match.group(1))
                            if lines:
                                filename = path_str.split('QR-ABSEN/')[-1]
                                target = output_dir + filename
                                with open(target, 'w', encoding='utf-8') as out_f:
                                    out_f.write('\n'.join(lines))
                                print(f"Recovered {filename}")
        except Exception as e:
            pass
