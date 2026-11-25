"""
Python (Flask) Birthday Website
All configuration, countdown calculation, Spotify URL parsing, and stage routing
are handled server-side in Python, paired with lightweight JS for persistent
opening-song playback across Stage 1 -> Stage 2 and Spotify IFrame API auto-pause.
"""

from datetime import datetime
import re
from urllib.parse import urlparse

from flask import Flask, redirect, render_template, url_for

# ============================================================================
# CENTRALIZED BIRTHDAY CONFIGURATION (EDIT EVERYTHING HERE)
# ============================================================================
BIRTHDAY_CONFIG = {
    # [EDIT HERE]: Name of the birthday person shown across all stages
    "RECIPIENT_NAME": "Sayangku, Igoo",

    # [EDIT HERE]: Target birthday date and time in ISO format: "YYYY-MM-DDTHH:MM:SS"
    # Uses the server's local time. Set a past date to auto-unlock directly to Stage 1.
    "BIRTHDAY_DATETIME": "2026-11-26T00:00:00",

    # [EDIT HERE]: Opening Spotify track revealed & highlighted right upon entering Stage 1
    "OPENING_SONG": {
        # [EDIT HERE]: Display title for the opening song
        "title": "Happy Birthday, my love <3",
        # [EDIT HERE]: Artist name for the opening song
        "artist": "A song for starting your special day",
        # [EDIT HERE]: Standard Spotify track link (https://open.spotify.com/track/<ID>?si=...) or raw Track ID
        "spotify_url": "https://open.spotify.com/intl-id/track/2x3vwXWuecPrRqgEUuSUJA?si=b8a495cc96384c38",
    },

    # [EDIT HERE]: Stage 1 (Post-Countdown Reveal) greeting headline (rendered 1st in Stage 1)
    "STAGE_1_TITLE": "Happy Birthday,",

    # [EDIT HERE]: Stage 1 message inside the interactive reveal card (rendered 2nd in Stage 1)
    "STAGE_1_MESSAGE": (
        "The countdown is finally over, and today belongs completely to you, my love, my dearest boyfie, sayangku. "
        "Take a deep breath, and lets take a step into "
        "a little space I made just to celebrate everything you are and every little things that i remember about you."
    ),

    # [EDIT HERE]: Stage 1 button label linking to Stage 2 (rendered 3rd in Stage 1)
    "STAGE_1_BUTTON_TEXT": "Continue to Next Page",

    # [EDIT HERE]: Stage 2 (Main Celebration Page) title (rendered 1st in Stage 2)
    "STAGE_2_TITLE": "A Little things for",

    # [EDIT HERE]: Stage 2 personal birthday letter (rendered 2nd in Stage 2; separate paragraphs with \n\n)
    "STAGE_2_MESSAGE": (
        "Happy birthday sayangnya akuu, another year around the sun and moonlight again, and somehow you keep making "
        "every ordinary day feel brighter just by being in it, terimakasiii banyak yaa sudah mau bertahan sejauh ini, sayangkuu, i really am proud of you.\n\n"
        "Thank you for every late-night laugh, every honest conversation, every usaha serta kesabaran kamu, dan every "
        "quiet moment that always turned into a precious memories ever. I hope this new chapter brings "
        "you gentle mornings with a serene night, big dreams coming true, and the exact same warmth you "
        "always give to everyone around you. You really are someone precious for everyone, jika semesta menitipkan harapan dan berkah dalam rupa manusia, bagiku, bentuk paling sempurnanya itu kamu, sayang.\n\n"
        "No matter how busy life gets, I will always be cheering the loudest for you, i will be the one who's always loving you the most and the purest. "
        "Make a wish, a lot of wishes yaaa — you deserve every greatest things in this world."
    ),

    # [EDIT HERE]: Polaroid / scrapbook photo gallery (place files inside static/images/)
    "PHOTOS": [
        {
            # [EDIT HERE]: Path inside static/ (e.g., "images/my-photo-1.jpg") or external URL
            "file": "images/one.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 1
            "caption": "This is when we have a deep talk for the first time, we really are disscusing about a lot of things that night ya wkwkwkwk (Asia Afrika, 7 Sept 2026, 07:47)",
        },
        {
            # [EDIT HERE]: Path inside static/ or external URL
            "file": "images/two.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 2
            "caption": "remember when we go to Braga?? kita barengan mulu dari awal ampe akhir, and we also listening to a lot of songs together while we walk (Braga, 11 Sept 2026, 20:20)",
        },
        {
            # [EDIT HERE]: Path inside static/ or external URL
            "file": "images/three.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 3
            "caption": "ANJAII, udah jadi anak telkom aja nih, proud of gantengnya akuu!! (Tel-U, 12 Sept 2026, 16:30)",
        },
        {
            # [EDIT HERE]: Path inside static/ or external URL
            "file": "images/four.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 4
            "caption": "Inget gasii ini kita mau pamer almet telkomm, bangga jadi anak telkom, bangga juga bisa jadi bagian dari your journey <3 (TSM, 12 Sept 2026, 20:44)",
        },
        {
            # [EDIT HERE]: Path inside static/ or external URL
            "file": "images/ten.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 4
            "caption": "Pulang ke Bogor buat nganterin aku konser, akhirnya drop juga :(, thanks a lot yaa sayangkuu (Bogor, 27 Sept 2026, 11:44)",
        },
        {
            # [EDIT HERE]: Path inside static/ or external URL
            "file": "images/six.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 4
            "caption": "inii, kita main truth or dare so we can know each other lebih dalamm, and turns out kita bisa nerima semua baik dan buruknya kita, terimakasii yaa sudah selalu jadi pendengar yang baikk (Hegarmanah, 4 Okto 2026, 05:49)",
        },
        {
            # [EDIT HERE]: Path inside static/ or external URL
            "file": "images/seven.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 4
            "caption": "TAHURAAAAA, OMGD OMGD OMGD, KAMUUU TAKUT MONYET IHHHHH (Tahura, 6 nov 2026, 13:50)",
        },
        {
            # [EDIT HERE]: Path inside static/ or external URL
            "file": "images/eight.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 4
            "caption": "Pose ABOUT YOU tuh (Tahura, 6 Nov 2026, 11:22)",
        },
        {
            # [EDIT HERE]: Path inside static/ or external URL
            "file": "images/nine.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 4
            "caption": "Gojek pribadii akuuu, terimakasii yaa selalu ada disetiap kegiatan akuuu (Tel-U, 15 Nov 2026, 11:11)",
        },
        {
            # [EDIT HERE]: Path inside static/ or external URL
            "file": "images/eleven.jpeg",
            # [EDIT HERE]: Handwritten-style caption below Photo 4
            "caption": "Ini cowo akuu yang ulang tahun hari inii, happiest birthday for you yaa sayang, semoga hari buruk mengurungkan niatnya untuk menghampiri kamu, dan hari baik itu selalu menanti kehadiran kamu, i love you the most <3",
        },
    ],

    # [EDIT HERE]: "3 Songs That Remind Me of You" section (rendered after Stage 2 Title & Message)
    "SONGS_REMIND_OF_YOU": [
        {
            # [EDIT HERE]: Song 1 title
            "title": "Anything You Want",
            # [EDIT HERE]: Song 1 artist
            "artist": "Reality Club",
            # [EDIT HERE]: Why Song 1 reminds you of them
            "note": "Kamu nyanyiin ini dan played this song waktu kita pertama kali di cafe 24 jam itu, and tiba tiba lagu ini ada kamunya.",
            # [EDIT HERE]: Song 1 Spotify track URL or raw Track ID
            "spotify_url": "https://open.spotify.com/intl-id/track/2QB8FwOszur18Ai7t2XnNi?si=4a1726243be64e01",
        },
        {
            # [EDIT HERE]: Song 2 title
            "title": "Ah",
            # [EDIT HERE]: Song 2 artist
            "artist": "Nadin Amizah",
            # [EDIT HERE]: Why Song 2 reminds you of them
            "note": "Lagu ini ngingetin aku kalau kamu adalah doa doaku yang didengar dan dikabulkan oleh tuhan, aku benar benar bersyukur kamu adalah wujud dari doa nya.",
            # [EDIT HERE]: Song 2 Spotify track URL or raw Track ID
            "spotify_url": "https://open.spotify.com/intl-id/track/0huV20ZR9HzTmBtXeYpEwD?si=82862a90ed624b43",
        },
        {
            # [EDIT HERE]: Song 3 title
            "title": "House Of Balloons",
            # [EDIT HERE]: Song 3 artist
            "artist": "The Weeknd",
            # [EDIT HERE]: Why Song 3 reminds you of them
            "note": "Uhmm, because you belong to me.",
            # [EDIT HERE]: Song 3 Spotify track URL or raw Track ID
            "spotify_url": "https://open.spotify.com/intl-id/track/50iiDJGpAPdr2VTrz999XA?si=badd859b49c945d6",
        },
    ],
}

app = Flask(__name__)


# ============================================================================
# PYTHON HELPER FUNCTIONS (SPOTIFY PARSER, COUNTDOWN, PHOTO PATHS)
# ============================================================================

def extract_spotify_track_id(spotify_input: str) -> str | None:
    """Extract a Spotify Track ID from a track URL, embed URL, URI, or raw ID."""
    if not spotify_input or not isinstance(spotify_input, str):
        return None

    trimmed = spotify_input.strip()

    # Raw Spotify Track ID (e.g. 71g0aW1XW2Uuh2Wn2e6U4q)
    if re.fullmatch(r"[A-Za-z0-9]{15,30}", trimmed):
        return trimmed

    # spotify:track:<ID> URI
    uri_match = re.match(r"^spotify:track:([A-Za-z0-9]+)$", trimmed, re.IGNORECASE)
    if uri_match:
        return uri_match.group(1)

    # https://open.spotify.com/track/<ID>?si=... or /intl-xx/track/<ID> or /embed/track/<ID>
    parsed = urlparse(trimmed)
    if "spotify.com" in parsed.netloc.lower():
        path_match = re.search(r"/(?:embed/)?track/([A-Za-z0-9]+)", parsed.path, re.IGNORECASE)
        if path_match:
            return path_match.group(1)

    fallback_match = re.search(r"track/([A-Za-z0-9]+)", trimmed, re.IGNORECASE)
    return fallback_match.group(1) if fallback_match else None


def to_spotify_embed_url(spotify_input: str) -> str | None:
    """Convert any Spotify track URL or ID into an embeddable Spotify player URL."""
    track_id = extract_spotify_track_id(spotify_input)
    if not track_id:
        return None
    return f"https://open.spotify.com/embed/track/{track_id}?utm_source=generator"


def compute_countdown(target_iso: str) -> dict:
    """Compute DD : HH : MM : SS remaining until BIRTHDAY_DATETIME."""
    try:
        target_dt = datetime.fromisoformat(target_iso)
    except (TypeError, ValueError):
        return {
            "invalid": True,
            "unlocked": False,
            "days": "00",
            "hours": "00",
            "minutes": "00",
            "seconds": "00",
            "target_display": "Invalid BIRTHDAY_DATETIME format in app.py",
        }

    remaining = int((target_dt - datetime.now()).total_seconds())
    target_display = target_dt.strftime("%a, %B %d, %Y at %I:%M %p")

    if remaining <= 0:
        return {
            "invalid": False,
            "unlocked": True,
            "days": "00",
            "hours": "00",
            "minutes": "00",
            "seconds": "00",
            "target_display": target_display,
        }

    days, rem = divmod(remaining, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    return {
        "invalid": False,
        "unlocked": False,
        "days": f"{days:02d}",
        "hours": f"{hours:02d}",
        "minutes": f"{minutes:02d}",
        "seconds": f"{seconds:02d}",
        "target_display": target_display,
    }


def resolve_photo_src(file_value: str) -> str:
    """Resolve either an external URL or a file path inside static/."""
    cleaned = (file_value or "").strip()
    if cleaned.startswith(("http://", "https://", "data:")):
        return cleaned
    if cleaned.startswith("static/"):
        cleaned = cleaned[len("static/"):]
    return url_for("static", filename=cleaned.lstrip("/"))


def build_stage_context(stage: int) -> dict:
    """Assemble template context from BIRTHDAY_CONFIG for the requested stage."""
    opening_song = BIRTHDAY_CONFIG["OPENING_SONG"]
    opening_track_id = extract_spotify_track_id(opening_song.get("spotify_url", ""))
    opening_embed_url = to_spotify_embed_url(opening_song.get("spotify_url", ""))

    photos = [
        {
            "src": resolve_photo_src(item.get("file", "")),
            "caption": item.get("caption", ""),
        }
        for item in BIRTHDAY_CONFIG.get("PHOTOS", [])
    ]

    songs = []
    for idx, song in enumerate(BIRTHDAY_CONFIG.get("SONGS_REMIND_OF_YOU", [])[:3]):
        track_id = extract_spotify_track_id(song.get("spotify_url", ""))
        songs.append(
            {
                "index": idx,
                "number": f"{idx + 1:02d}",
                "title": song.get("title", f"Track {idx + 1}"),
                "artist": song.get("artist", ""),
                "note": song.get("note", ""),
                "track_id": track_id,
                "spotify_uri": f"spotify:track:{track_id}" if track_id else "",
                "embed_url": to_spotify_embed_url(song.get("spotify_url", "")),
            }
        )

    raw_message = BIRTHDAY_CONFIG.get("STAGE_2_MESSAGE", "")
    stage2_paragraphs = [p.strip() for p in re.split(r"\n{2,}", raw_message) if p.strip()]

    return {
        "stage": stage,
        "config": BIRTHDAY_CONFIG,
        "opening_song": opening_song,
        "opening_track_id": opening_track_id,
        "opening_spotify_uri": f"spotify:track:{opening_track_id}" if opening_track_id else "",
        "opening_embed_url": opening_embed_url,
        "photos": photos,
        "songs": songs,
        "stage2_paragraphs": stage2_paragraphs,
    }


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route("/")
def index():
    """Stage 0: Server-rendered countdown screen (auto-redirects once unlocked)."""
    countdown = compute_countdown(BIRTHDAY_CONFIG.get("BIRTHDAY_DATETIME", ""))
    if countdown["unlocked"]:
        return redirect(url_for("stage1"))

    context = build_stage_context(stage=0)
    context["countdown"] = countdown
    return render_template("index.html", **context)


@app.route("/unlock", methods=["GET", "POST"])
def unlock():
    """Preview / unlock route redirecting directly into Stage 1."""
    return redirect(url_for("stage1"))


@app.route("/stage1", methods=["GET", "POST"])
def stage1():
    """Stage 1: Post-countdown reveal with highlighted opening Spotify song."""
    context = build_stage_context(stage=1)
    return render_template("index.html", **context)


@app.route("/stage2", methods=["GET", "POST"])
def stage2():
    """Stage 2: Main celebration page with message, photos, and 3 Spotify songs."""
    context = build_stage_context(stage=2)
    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
