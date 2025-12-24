"""
Frozen Signal - Narrative System
Documents, audio logs, and multiple endings
"""

from .constants import EndingFlag


# Documents found throughout the base
DOCUMENTS = {
    "note_wake": {
        "title": "PERSONAL NOTE",
        "content": """Day 1 of awakening.

I don't know how long I was asleep. The chronometer is frozen at 03:47.
The others... I found Volkov in the corridor. Still standing. Frozen solid.
His face - he saw something. Something that made him try to run.

The emergency beacon is dead. Radio picks up only static.
Sometimes I hear patterns in it. Almost like words.

I need to find the communications room. There has to be a way out.

- K.S.""",
        "flag": None
    },

    "note_drilling": {
        "title": "DRILLING LOG - DAY 47",
        "content": """Depth: 3,847 meters. Dr. Volkov insists we continue.
The ice here is strange. Too old. The spectrometer readings make no sense.

Today the drill bit hit something that wasn't ice. Not rock either.
It sang when we struck it. The whole shaft resonated.

Morale is low. Petrov says he hears whispers from the shaft at night.
I told him it's just wind through the tunnels.

I'm not sure I believe that anymore.

- Chief Engineer Markova""",
        "flag": EndingFlag.DISCOVERED_SIGNAL
    },

    "note_signal": {
        "title": "CLASSIFIED - SIGNAL ANALYSIS",
        "content": """TO: Director Orlov
FROM: Dr. Volkov
RE: The Signal

Analysis confirms the transmission is not natural.
The pattern repeats every 73.4 seconds. Mathematical.
Origin point: approximately 4km beneath the surface.

We've been listening for decades. Moscow wants to know what's down there.
I've requested additional drilling equipment and personnel.

This could change everything we know about our place in the universe.
Or it could end it.

[REMAINDER CLASSIFIED - LEVEL 5 CLEARANCE REQUIRED]""",
        "flag": EndingFlag.DISCOVERED_SIGNAL
    },

    "note_subjects": {
        "title": "MEDICAL LOG - SUBJECT NOTES",
        "content": """Subject 7 expired at 0300 hours.
Like the others, exposure to the artifact caused rapid neural degradation.
But before death, Subject 7 spoke in a language none of us recognized.
Dr. Petrov's recorder captured it. When played back, three researchers
became catatonic.

The artifact pulses stronger now. It knows we're listening.

Recommendation: Cease all contact experiments.

This was rejected by Director Orlov. New subjects arrive tomorrow.

May God forgive us.""",
        "flag": EndingFlag.FREED_SUBJECTS
    },

    "note_escape": {
        "title": "EVACUATION NOTICE",
        "content": """TO ALL PERSONNEL:

Emergency evacuation order CANCELED by Director Orlov.
Containment breach in Sector 7 has been "resolved."

The elevator to surface is now RESTRICTED.
Only personnel with Level 4 clearance may access.

Do not listen to the broadcasts from the deep excavation.
Do not look directly at affected personnel.
Report any unusual thoughts immediately to Medical.

Glory to the motherland. The project continues.

[This notice has been partially burned]""",
        "flag": EndingFlag.ESCAPED
    },

    "note_finale": {
        "title": "LAST TRANSMISSION",
        "content": """They weren't drilling for oil. They were listening.
And something answered.

It's been down there for millions of years. Waiting.
Patient. So patient. Dreaming in the ice.

Our signal woke it. Or maybe we ARE the signal.
Receivers built to hear its call.

I understand now. The cold isn't the enemy.
It was keeping us safe. Keeping IT asleep.

The reactor. If I can shut down the reactor...
The cold will return. It will sleep again.

Or I can answer. Finally answer.

The choice isn't mine to make. It's yours.

- Final entry, unknown author""",
        "flag": None
    },

    "note_reactor": {
        "title": "REACTOR CONTROL MANUAL",
        "content": """EMERGENCY SHUTDOWN PROCEDURE:

1. Insert REACTOR KEY (Located in Director's Office)
2. Enter authorization code: 7-3-4-7
3. Pull SCRAM lever
4. Evacuate immediately - core will reach critical cold in 3 minutes

WARNING: Shutdown will terminate all life support.
Base temperature will drop to -60C within 1 hour.

Only authorized personnel may initiate shutdown.
Unauthorized shutdown is punishable by [text obscured]""",
        "flag": None
    }
}

# Audio logs (stored as text with metadata)
AUDIO_LOGS = {
    "log_intro": {
        "title": "RECORDING 001",
        "speaker": "Unknown Voice",
        "content": """[STATIC]
...can anyone hear me? This is... [STATIC]
...been trying to reach the surface for...
The others are changing. I can see it in their eyes.
They look at the walls like they can see through them.
Down. They're always looking down.
[STATIC]
...if you're hearing this, don't go deeper. Don't...
[RECORDING ENDS]""",
        "flag": None
    },

    "log_volkov": {
        "title": "DR. VOLKOV - PERSONAL LOG",
        "speaker": "Dr. Alexei Volkov",
        "content": """Day 89 of the expedition.

We've made contact. Not with radio waves - with thought.
The artifact... it speaks directly to the mind.
At first just fragments. Images of cold stars. Dead worlds.
But now... now I understand its purpose.

It's a beacon. A lighthouse for things that swim between stars.
And we've been shining it for fifty years.

They're coming. They were always coming.
We just told them where to land.""",
        "flag": EndingFlag.DISCOVERED_SIGNAL
    },

    "log_petrov": {
        "title": "ENGINEER PETROV - FINAL LOG",
        "speaker": "Engineer Yuri Petrov",
        "content": """[HEAVY BREATHING]
I saw what happened to Markova.
One moment she was checking the drill assembly.
The next she was... folding. Like paper.
Her eyes were still moving when they took her below.

I'm sealing myself in the storage room.
The keycard is hidden under the third crate.
If anyone finds this...

[DISTANT SOUND - LIKE SINGING]

Oh God. It's beautiful. It's so beautiful.
I understand now. We're not being killed.
We're being translated.

[RECORDING ENDS]""",
        "flag": EndingFlag.SAVED_SURVIVOR
    }
}


class NarrativeManager:
    """Manages narrative state and endings"""

    def __init__(self):
        self.documents_found = set()
        self.audio_logs_heard = set()
        self.flags = set()
        self.choices_made = {}

        # Ending tracking
        self.ending_reached = None

    def find_document(self, doc_id):
        """Mark a document as found"""
        if doc_id in DOCUMENTS:
            self.documents_found.add(doc_id)
            doc = DOCUMENTS[doc_id]
            if doc.get('flag'):
                self.flags.add(doc['flag'])
            return doc
        return None

    def hear_audio_log(self, log_id):
        """Mark an audio log as heard"""
        if log_id in AUDIO_LOGS:
            self.audio_logs_heard.add(log_id)
            log = AUDIO_LOGS[log_id]
            if log.get('flag'):
                self.flags.add(log['flag'])
            return log
        return None

    def add_flag(self, flag):
        """Add a narrative flag"""
        self.flags.add(flag)

    def has_flag(self, flag):
        """Check if a flag has been set"""
        return flag in self.flags

    def make_choice(self, choice_id, option):
        """Record a narrative choice"""
        self.choices_made[choice_id] = option

    def get_document(self, doc_id):
        """Get document content"""
        return DOCUMENTS.get(doc_id)

    def get_audio_log(self, log_id):
        """Get audio log content"""
        return AUDIO_LOGS.get(log_id)

    def check_all_logs_found(self):
        """Check if all documents and logs have been found"""
        all_docs = len(self.documents_found) >= len(DOCUMENTS)
        all_logs = len(self.audio_logs_heard) >= len(AUDIO_LOGS)

        if all_docs and all_logs:
            self.flags.add(EndingFlag.READ_ALL_LOGS)

        return all_docs and all_logs

    def determine_ending(self):
        """Determine which ending the player gets based on flags"""
        self.check_all_logs_found()

        # Ending priority (checked in order)
        # 1. The Embrace - player chose to answer the signal
        if EndingFlag.EMBRACED in self.flags:
            return "ending_embrace"

        # 2. The Silence - destroyed the transmitter, stopped the signal
        if EndingFlag.DESTROYED_TRANSMITTER in self.flags:
            if EndingFlag.SAVED_SURVIVOR in self.flags:
                return "ending_silence_survivor"
            return "ending_silence"

        # 3. The Escape - made it out alive
        if EndingFlag.ESCAPED in self.flags:
            if EndingFlag.READ_ALL_LOGS in self.flags:
                return "ending_truth"
            return "ending_escape"

        # 4. Default - player died or gave up
        return "ending_lost"


# Ending content
ENDINGS = {
    "ending_embrace": {
        "title": "THE EMBRACE",
        "content": """You reached out with your mind, as they taught you.
And something answered.

The cold that had gripped your body faded to nothing.
You felt yourself expanding, unfolding, becoming more than flesh.

The signal wasn't a warning. It was an invitation.
And you accepted.

In the depths beneath the ice, you joined the chorus.
Another voice in a song that spans galaxies.
Another receiver, now a transmitter.

Others will come. They always do.
And you will be waiting to welcome them home.

THE END - EMBRACE ENDING"""
    },

    "ending_silence": {
        "title": "THE SILENCE",
        "content": """The reactor's emergency shutdown plunged the base into darkness.
True darkness. True cold.

As the temperature plummeted, you felt something else fade.
The whispers. The constant pressure at the edge of your thoughts.
Silence, for the first time in what felt like forever.

In the deep excavation, the crystal's glow dimmed and died.
Whatever slumbered there returned to its ancient dream.

You didn't survive. No one could, in that cold.
But in your final moments, you heard nothing.
Blissful, empty nothing.

Some prices are worth paying.

THE END - SILENCE ENDING"""
    },

    "ending_silence_survivor": {
        "title": "THE SILENCE (Petrov Survived)",
        "content": """The reactor died, and with it, the signal.
The crystal fell silent. The whispers stopped.

But you weren't alone.

In the storage room, you found Petrov. Still human. Still sane.
Together, you wrapped yourselves in thermal gear and walked.
Through the frozen tunnels. Past the still forms of what were once colleagues.
Up, toward the surface.

The rescue team found you three days later.
Frostbitten, hypothermic, but alive.

Neither of you spoke of what you saw.
Some truths aren't meant to be shared.

THE END - SILENCE WITH SURVIVOR"""
    },

    "ending_truth": {
        "title": "THE TRUTH",
        "content": """You read every document. Heard every log.
Piece by piece, you assembled the terrible truth.

They came to Antarctica seeking oil. They found a signal.
For fifty years, they listened. Experimented. Sacrificed.
All to understand a message from something incomprehensible.

Now you carry that knowledge out into the world.
The evidence in your pack. The truth in your mind.

Will anyone believe you? Perhaps not.
But the signal is still broadcasting. Others will hear it.
And they'll need to know what you know.

The truth isn't a weapon. It's a warning.

THE END - TRUTH ENDING"""
    },

    "ending_escape": {
        "title": "THE ESCAPE",
        "content": """You ran.

Through frozen corridors and past things that used to be human.
You didn't stop to understand. Didn't try to be a hero.
You found the elevator, entered the code, and ascended.

The surface was a wall of white. Blinding snow and screaming wind.
But it was real. It was outside.

You walked until you collapsed. Until rescue found you.

In the hospital, you told them nothing.
What could you say? What would they believe?

Outpost Erebus remains buried in the ice.
And some nights, when the wind is right,
you swear you can still hear it calling.

THE END - ESCAPE ENDING"""
    },

    "ending_lost": {
        "title": "SIGNAL LOST",
        "content": """The cold claimed you in the end.

Perhaps it was exposure. Perhaps something worse.
Your final thoughts were of warmth. Of home. Of a life above the ice.

But even as consciousness faded, you heard it.
The signal. Constant. Patient. Eternal.

It would wait for the next one.
It always did.

TRANSMISSION ENDED

THE END - LOST ENDING"""
    }
}


def get_ending_content(ending_id):
    """Get the full ending content"""
    return ENDINGS.get(ending_id, ENDINGS["ending_lost"])
