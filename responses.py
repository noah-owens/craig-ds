import random

RESPONSES = {
    "now_playing": [
        "*Craig's reluctantly spinning **{title}** without making eye contact.*",
        "Did you know that Tame Impala is just one guy? Anyway, here's **{title}**.",
        "Here's **{title}**, it's no Arctic Monkeys.",
        "Ugh. (**{title}**)",
        "This one'll get the whole retirement home shuffling -- now playing **{title}**",
    ],
    "not_connected": [
        "I'm not gonna DJ for no-one. Join a voice channel.",
        "*Craig looks around in confusion.*"
    ],
    "volume changed": [
        "*Craig's volume is now set to {volume}%. He still isn't dancing.*"
        "*Volume adjusted to {volume}%.*",
    ],
    "help": [
        "**Craig's Command List**\n"
        "`!join [channel]` - Craig joins your voice channel.\n"
        "`!play [file]` - Plays a local audio file.\n"
        "`!yt [url]` - Downloads and plays a YouTube video.\n"
        "`!stream [url]` - Streams audio from YouTube without downloading.\n"
        "`!volume [0-100]` - Adjusts Craig's volume.\n"
        "`!stop` - Banishes Craig."
    ]
}

def get_response(key, **kwargs):
    """Returns a formatted random response for a given key."""
    template = random.choice(RESPONSES.get(key, ["*Craig has nothing to say.*"]))
    return template.format(**kwargs)