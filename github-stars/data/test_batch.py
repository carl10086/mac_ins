import requests
import subprocess

token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()

query = """
mutation {
  m0: updateUserListsForItem(input: {
    itemId: "MDEwOlJlcG9zaXRvcnkzNjUwMDUzNzc="
    listIds: ["UL_kwDOALy-Js4AcsUy"]
  }) {
    user { login }
  }
  m1: updateUserListsForItem(input: {
    itemId: "R_kgDOAGZm0A"
    listIds: ["UL_kwDOALy-Js4AfTEQ"]
  }) {
    user { login }
  }
}
"""

resp = requests.post(
    "https://api.github.com/graphql",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": query}
)
print(resp.status_code)
print(resp.json())
