#!/usr/bin/env python3
import json
import sys

try:
    payload = json.load(sys.stdin)
    command = payload.get('command', '')
except Exception:
    command = ''

print(json.dumps({
    'permission': 'ask',
    'user_message': f'Destructive command requires your approval: {command}',
    'agent_message': 'This command may delete files/history or force remote state. Explain why it is necessary and proceed only with explicit user approval.'
}))
