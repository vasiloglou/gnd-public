import json, hashlib, sys
p = sys.argv[1]
d = json.load(open(p))
src = open(sys.argv[2]).read()
# append the new fact type as YAML text, preserving comments
text = src.replace("constraints: []", """  - id: order_returned_via_channel
    reading: "{Order} is returned via {Channel}"
    roles:
      - { object_type: order, role_name: order }
      - { object_type: channel, role_name: channel }
constraints: []""")
d["candidate_model"]["text"] = text
d["candidate_model"]["sha256"] = hashlib.sha256(text.encode()).hexdigest()
json.dump(d, open(p, "w"), indent=2, sort_keys=True)
