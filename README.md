# Craig-DS

### A simple discord music bot that just really couldn't care less about your music taste. 

*Every song you queue is truly an inconvenience to him.*

- Supports Youtube Links w/ Stream and Download
  - Truncates Youtube playlist links to the first entry (playlist support not currently planned)
- Supports local files 

## Host Craig on your own:

Requires Python3 to be installed.

Create an application in the [Discord developer portal](https://discord.com/developers/applications) ensure that the bot has permission to read messages, send messages, and speak in voice. 

Copy (BUT DO NOT SHARE) your unique bot token.

In your local craig-ds directory:

```
pip install -r requirements.txt
```

```
echo "TOKEN='[paste your bot token here]'" > .env
```

Generate a discord bot invitation link in the developer portal and add to your server.

Run craig-ds.py to host the bot from your machine

Use command `!help` to learn what Craig is capable of.