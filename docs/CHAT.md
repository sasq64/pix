- When the chat starts, the user id is set. The first time this happen, it is randomly generated and saved to disk.
- When chat starts, the current user always connect to his own room, which has the same name as the user ID.
- A user can join someone elses chat just by knowing the users ID.
- A user can only be in one chat at a time.

Chat

  connect(id)

TYPE: -> Send to server
AI RESPONSE: -> Send to server

From Server: If not you and not AI: Send to AI

Add channel target; ALL or <id>

Show target before prompt. Default AI when one user, defalt CHAN when more than one

MAYBE: Summarize non AI lines into code related info when needed


