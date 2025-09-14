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
        "*Craig looks around in confusion.*",
    ],
    "volume_changed": [
        "*Craig's volume is now set to {volume}%. He still isn't dancing.*",
        "*Volume adjusted to {volume}%.*",
    ],
    "queue_empty": [
        "Thank God. (Queue is empty)",
        "Our long national nightmare is over. (Queue is empty)",
    ],
    "add_queue": [
        "You sure? Okay. Added {len} tracks to queue.",
    ],
    "skip": [
        "*Craig skipped that one. You're welcome.*",
    ],
    "not_playing": [
        "You serious? Nothing's even playing.",
    ],
    "upcoming": [
        "Who made this list, a bunch of jocks? \n {queue_text}",
    ],
    "queue_clear": [
        "MAKE UP YOUR MIND (queue cleared)",
        "*Craig cleared the queue. Please, no more.*",
    ],
    "max_entries": [
        "*Craig only added {max} tracks to the queue. The man has limits.",
    ]
}

def get_response(key, **kwargs):
    """Returns a formatted random response for a given key."""
    template = random.choice(RESPONSES.get(key, ["*Craig has nothing to say.*"]))
    return template.format(**kwargs)