import json
raw = '''{
    "code": "def foo():
    print('hello')"
}'''
try:
    print('Default loads:', json.loads(raw))
except Exception as e:
    print('Default loads failed:', e)
try:
    print('Strict=False loads:', json.loads(raw, strict=False))
except Exception as e:
    print('Strict=False loads failed:', e)
