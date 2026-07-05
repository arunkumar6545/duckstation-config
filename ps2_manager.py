#!/usr/bin/env python3
"""
PS2 Game Manager
================
  +N  → Download game (or launch if already downloaded)
  -N  → Delete game (with confirmation)
   0  → Quit
"""

import os, sys, json, subprocess, shutil, re, time, zipfile, ssl
from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import URLError, HTTPError

# Fix macOS SSL certificate verification issue
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# ─── Config ────────────────────────────────────────────────────────────────────
GAMES_DIR  = os.path.expanduser("~/Games/PS2")
PCSX2_APP  = "/Applications/PCSX2.app"

# ANSI colours
R  = "\033[91m"; G  = "\033[92m"; Y  = "\033[93m"
B  = "\033[94m"; C  = "\033[96m"; M  = "\033[95m"
BD = "\033[1m";  DM = "\033[2m";  RS = "\033[0m"

# ─── Top 50 PS2 Games ──────────────────────────────────────────────────────────
# (rank, title, year, genre, rating/10, archive_search_query, filename_keywords)
GAMES = [
    ( 1, "Shadow of the Colossus",             2005, "Action-Adventure",  9.6, "Shadow of the Colossus USA PS2",             ["shadow", "colossus"]),
    ( 2, "God of War II",                       2007, "Action-Adventure",  9.5, "God of War II USA PS2 ISO",                  ["god of war ii", "god of war 2"]),
    ( 3, "God of War",                          2005, "Action-Adventure",  9.4, "God of War USA PS2 SCUS",                    ["god of war"]),
    ( 4, "Metal Gear Solid 3: Snake Eater",     2004, "Stealth",           9.4, "Metal Gear Solid 3 Snake Eater USA PS2",     ["metal gear solid 3", "snake eater"]),
    ( 5, "Grand Theft Auto: San Andreas",       2004, "Open World",        9.3, "Grand Theft Auto San Andreas PS2 USA",       ["san andreas"]),
    ( 6, "Grand Theft Auto: Vice City",         2002, "Open World",        9.2, "Grand Theft Auto Vice City PS2 USA",         ["vice city"]),
    ( 7, "Resident Evil 4",                     2005, "Survival Horror",   9.2, "Resident Evil 4 PS2 USA ISO",               ["resident evil 4"]),
    ( 8, "Ico",                                 2001, "Action-Adventure",  9.1, "Ico PS2 USA ISO SCUS",                       ["ico"]),
    ( 9, "Okami",                               2006, "Action-Adventure",  9.1, "Okami PS2 USA ISO",                          ["okami"]),
    (10, "Final Fantasy XII",                   2006, "RPG",               9.0, "Final Fantasy XII PS2 USA ISO",              ["final fantasy xii", "final fantasy 12"]),
    (11, "Kingdom Hearts II",                   2005, "Action-RPG",        9.0, "Kingdom Hearts II PS2 USA ISO",              ["kingdom hearts ii", "kingdom hearts 2"]),
    (12, "Kingdom Hearts",                      2002, "Action-RPG",        8.9, "Kingdom Hearts PS2 USA ISO SLUS",            ["kingdom hearts"]),
    (13, "Dragon Quest VIII",                   2004, "RPG",               8.9, "Dragon Quest VIII PS2 USA ISO",              ["dragon quest viii", "dragon quest 8"]),
    (14, "Devil May Cry 3: Special Edition",    2005, "Action",            8.8, "Devil May Cry 3 Special Edition PS2 USA",    ["devil may cry 3"]),
    (15, "Metal Gear Solid 2: Sons of Liberty", 2001, "Stealth",           8.8, "Metal Gear Solid 2 Sons of Liberty PS2 USA", ["metal gear solid 2", "sons of liberty"]),
    (16, "Jak and Daxter",                      2001, "Platformer",        8.7, "Jak and Daxter PS2 USA ISO",                 ["jak and daxter", "jak daxter"]),
    (17, "Ratchet & Clank: Up Your Arsenal",    2004, "Platformer",        8.7, "Ratchet Clank Up Your Arsenal PS2 USA",      ["up your arsenal", "ratchet clank 3"]),
    (18, "Jak II",                              2003, "Action-Adventure",  8.6, "Jak II PS2 USA ISO",                         ["jak ii", "jak 2"]),
    (19, "Burnout 3: Takedown",                 2004, "Racing",            8.6, "Burnout 3 Takedown PS2 USA ISO",             ["burnout 3", "takedown"]),
    (20, "Gran Turismo 4",                      2004, "Racing",            8.6, "Gran Turismo 4 PS2 USA ISO",                 ["gran turismo 4"]),
    (21, "Tekken 5",                            2004, "Fighting",          8.5, "Tekken 5 PS2 USA SLUS-21059",               ["tekken 5"]),
    (22, "SoulCalibur III",                     2005, "Fighting",          8.5, "SoulCalibur III PS2 USA ISO",                ["soulcalibur iii", "soulcalibur 3", "soul calibur"]),
    (23, "Prince of Persia: Sands of Time",     2003, "Action-Adventure",  8.5, "Prince of Persia Sands of Time PS2 USA",    ["prince of persia", "sands of time"]),
    (24, "Need for Speed: Most Wanted",         2005, "Racing",            8.4, "Need for Speed Most Wanted PS2 USA",         ["most wanted", "nfs"]),
    (25, "Ratchet & Clank: Going Commando",     2003, "Platformer",        8.4, "Ratchet Clank Going Commando PS2 USA",       ["going commando", "ratchet clank 2"]),
    (26, "Star Wars Battlefront II",            2005, "Shooter",           8.4, "Star Wars Battlefront II PS2 USA ISO",       ["battlefront ii", "battlefront 2"]),
    (27, "Tekken Tag Tournament",               2000, "Fighting",          8.3, "Tekken Tag Tournament PS2 USA ISO",          ["tekken tag"]),
    (28, "Onimusha: Warlords",                  2001, "Action",            8.3, "Onimusha Warlords PS2 USA ISO",              ["onimusha"]),
    (29, "Ace Combat 5: The Unsung War",        2004, "Flight Action",     8.3, "Ace Combat 5 Unsung War PS2 USA ISO",        ["ace combat 5"]),
    (30, "Twisted Metal Black",                 2001, "Vehicular Combat",  8.3, "Twisted Metal Black PS2 USA ISO",            ["twisted metal"]),
    (31, "Gradius V",                           2004, "Shoot em up",       8.2, "Gradius V PS2 USA ISO",                      ["gradius v", "gradius 5"]),
    (32, "Contra: Shattered Soldier",           2002, "Run and Gun",       8.2, "Contra Shattered Soldier PS2 USA ISO",       ["contra shattered"]),
    (33, "Metal Slug Anthology",                2006, "Run and Gun",       8.2, "Metal Slug Anthology PS2 USA",               ["metal slug anthology", "metal slug"]),
    (34, "Devil May Cry",                       2001, "Action",            8.2, "Devil May Cry PS2 USA ISO SLUS",             ["devil may cry"]),
    (35, "Tekken 4",                            2002, "Fighting",          8.1, "Tekken 4 PS2 USA ISO",                       ["tekken 4"]),
    (36, "Gran Turismo 3: A-Spec",              2001, "Racing",            8.1, "Gran Turismo 3 A-Spec PS2 USA ISO",          ["gran turismo 3"]),
    (37, "SSX Tricky",                          2001, "Extreme Sports",    8.1, "SSX Tricky PS2 USA ISO",                     ["ssx tricky"]),
    (38, "Tony Hawk's Pro Skater 3",            2001, "Extreme Sports",    8.1, "Tony Hawk Pro Skater 3 PS2 USA ISO",         ["tony hawk", "pro skater 3"]),
    (39, "Ratchet & Clank",                     2002, "Platformer",        8.0, "Ratchet and Clank PS2 USA ISO",              ["ratchet clank"]),
    (40, "Crash Bandicoot: Wrath of Cortex",    2001, "Platformer",        8.0, "Crash Bandicoot Wrath of Cortex PS2 USA",    ["wrath of cortex", "crash bandicoot"]),
    (41, "Sly Cooper and the Thievius Raccoonus",2002,"Stealth-Platform",  8.0, "Sly Cooper Thievius Raccoonus PS2 USA",      ["sly cooper"]),
    (42, "Silent Hill 2",                       2001, "Survival Horror",   8.0, "Silent Hill 2 PS2 USA ISO",                  ["silent hill 2"]),
    (43, "Silent Hill 3",                       2003, "Survival Horror",   7.9, "Silent Hill 3 PS2 USA ISO",                  ["silent hill 3"]),
    (44, "Castlevania: Curse of Darkness",      2005, "Action",            7.9, "Castlevania Curse of Darkness PS2 USA",      ["castlevania", "curse of darkness"]),
    (45, "Guitar Hero II",                      2006, "Rhythm",            7.9, "Guitar Hero II PS2 USA ISO",                 ["guitar hero ii", "guitar hero 2"]),
    (46, "Dynasty Warriors 4",                  2003, "Hack and Slash",    7.8, "Dynasty Warriors 4 PS2 USA ISO",             ["dynasty warriors 4"]),
    (47, "Mortal Kombat: Armageddon",           2006, "Fighting",          7.8, "Mortal Kombat Armageddon PS2 USA ISO",       ["mortal kombat armageddon"]),
    (48, "Ace Combat 4: Shattered Skies",       2001, "Flight Action",     7.8, "Ace Combat 4 Shattered Skies PS2 USA",       ["ace combat 4"]),
    (49, "Champions of Norrath",                2004, "Action-RPG",        7.7, "Champions of Norrath PS2 USA ISO",           ["champions of norrath"]),
    (50, "Baldur's Gate: Dark Alliance",        2001, "Action-RPG",        7.7, "Baldurs Gate Dark Alliance PS2 USA",         ["baldurs gate", "dark alliance"]),
]

# ─── Helpers ───────────────────────────────────────────────────────────────────

def clear():
    os.system("clear")

def disk_free():
    try:
        r = subprocess.run(["df", "-h", os.path.expanduser("~")], capture_output=True, text=True)
        parts = r.stdout.strip().split("\n")[1].split()
        return f"{G}{parts[3]}{RS}" if len(parts) >= 4 else "?"
    except Exception:
        return "?"

def normalize(s):
    return re.sub(r"[^\w\s]", "", s.lower())

def get_iso_files():
    """Return {normalized_name: full_path} for all ISOs in GAMES_DIR."""
    result = {}
    if not os.path.isdir(GAMES_DIR):
        return result
    for f in os.listdir(GAMES_DIR):
        if f.lower().endswith(".iso"):
            result[normalize(os.path.splitext(f)[0])] = os.path.join(GAMES_DIR, f)
    return result

def find_iso(keywords, iso_map):
    """Return path if any keyword matches a downloaded ISO, else None."""
    for kw in keywords:
        kw_n = normalize(kw)
        for name, path in iso_map.items():
            if kw_n in name:
                return path
    return None

def stars(rating):
    full  = int(round(rating / 2))
    empty = 5 - full
    return f"{Y}{'★' * full}{DM}{'☆' * empty}{RS}"

# ─── Archive.org Search ────────────────────────────────────────────────────────

def search_archive(query, rows=10):
    """Search archive.org, return [(identifier, title), ...]."""
    url = (
        "https://archive.org/advancedsearch.php"
        f"?q={quote(query)}+mediatype%3Asoftware"
        "&fl[]=identifier&fl[]=title&output=json"
        f"&rows={rows}&page=1"
    )
    try:
        req = Request(url, headers={"User-Agent": "PS2Manager/1.0"})
        with urlopen(req, timeout=15, context=SSL_CTX) as r:
            data = json.load(r)
            docs = data.get("response", {}).get("docs", [])
            return [(d["identifier"], d.get("title", "")) for d in docs]
    except Exception as e:
        print(f"{R}Search error: {e}{RS}")
        return []

def best_file(identifier):
    """Return (filename, size_bytes) for the best ISO/7z/zip in an archive item."""
    url = f"https://archive.org/metadata/{identifier}"
    try:
        req = Request(url, headers={"User-Agent": "PS2Manager/1.0"})
        with urlopen(req, timeout=15, context=SSL_CTX) as r:
            data = json.load(r)
        files = data.get("files", [])
        for ext in (".iso", ".7z", ".zip"):
            for f in files:
                name = f.get("name", "")
                if name.lower().endswith(ext) and not name.startswith("_"):
                    return name, int(f.get("size", 0))
    except Exception as e:
        print(f"{R}Metadata error: {e}{RS}")
    return None, 0

def pick_identifier(results, title):
    """Choose best archive.org result, preferring USA/NTSC."""
    title_words = [w.lower() for w in title.split() if len(w) > 3]
    # Score each result: prefer USA/NTSC + title word matches
    def score(item):
        ident, ititle = item
        s = 0
        combined = (ident + " " + ititle).lower()
        if any(k in combined for k in ["usa", "ntsc", "us"]):
            s += 10
        s += sum(1 for w in title_words if w in combined)
        return s
    results = sorted(results, key=score, reverse=True)
    return results[0][0] if results else None

# ─── Download & Extract ────────────────────────────────────────────────────────

def download_game(game):
    _, title, _, _, _, search_query, _ = game

    print(f"\n{BD}{C}Searching archive.org for: {title}{RS}")
    results = search_archive(search_query)
    if not results:
        print(f"{R}No results found. Try again later.{RS}")
        input("\nPress Enter to continue...")
        return

    # Try up to 5 identifiers to find one with a downloadable file
    identifier = None
    filename = None
    size_bytes = 0
    for ident, _ in results[:5]:
        fn, sz = best_file(ident)
        if fn:
            identifier, filename, size_bytes = ident, fn, sz
            break

    if not identifier:
        identifier = pick_identifier(results, title)
        filename, size_bytes = best_file(identifier) if identifier else (None, 0)

    if not filename:
        print(f"{R}No downloadable file found in search results.{RS}")
        input("\nPress Enter to continue...")
        return

    size_gb = size_bytes / (1024 ** 3) if size_bytes else 0
    print(f"  Source : {identifier}")
    print(f"  File   : {filename}  ({size_gb:.1f} GB)")

    os.makedirs(GAMES_DIR, exist_ok=True)
    dest = os.path.join(GAMES_DIR, filename)
    url  = f"https://archive.org/download/{identifier}/{quote(filename)}"

    print(f"\n{Y}Downloading — press Ctrl+C to pause/resume later{RS}\n")
    ret = subprocess.run([
        "curl", "-L", "--retry", "3", "--retry-delay", "5",
        "-C", "-", "--progress-bar",
        "-o", dest, url
    ])

    if ret.returncode != 0:
        print(f"\n{R}Download failed or interrupted.{RS}")
        input("\nPress Enter to continue...")
        return

    print(f"\n{G}Download complete!{RS}")

    # Extract
    final = os.path.join(GAMES_DIR, f"{title}.iso")
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".7z":
        print(f"{Y}Extracting .7z archive...{RS}")
        subprocess.run(["7z", "e", dest, f"-o{GAMES_DIR}", "-y"], check=True)
        os.remove(dest)
        # Rename extracted ISO
        for f in os.listdir(GAMES_DIR):
            fp = os.path.join(GAMES_DIR, f)
            if f.lower().endswith(".iso") and fp != final:
                os.rename(fp, final)
                break

    elif ext == ".zip":
        print(f"{Y}Extracting .zip archive...{RS}")
        try:
            with zipfile.ZipFile(dest) as z:
                for member in z.namelist():
                    if member.lower().endswith(".iso"):
                        z.extract(member, GAMES_DIR)
                        extracted = os.path.join(GAMES_DIR, member)
                        os.makedirs(os.path.dirname(final) or GAMES_DIR, exist_ok=True)
                        shutil.move(extracted, final)
                        break
        except zipfile.BadZipFile:
            print(f"{R}ZIP corrupt — trying ditto...{RS}")
            subprocess.run(["ditto", "-x", "-k", dest, GAMES_DIR])
        os.remove(dest)
        # Clean empty dirs left by zip
        for item in os.listdir(GAMES_DIR):
            p = os.path.join(GAMES_DIR, item)
            if os.path.isdir(p):
                shutil.rmtree(p, ignore_errors=True)

    elif ext == ".iso" and dest != final:
        os.rename(dest, final)

    if os.path.exists(final):
        size = os.path.getsize(final) / (1024 ** 3)
        print(f"\n{BD}{G}'{title}' ready!  ({size:.1f} GB){RS}")
        print(f"  Path: {final}")
    else:
        print(f"\n{Y}Download done. Check {GAMES_DIR} for the ISO.{RS}")

    input("\nPress Enter to continue...")

def launch_game(iso_path, title):
    print(f"\n{G}Launching {title} in PCSX2...{RS}")
    subprocess.Popen(["open", "-a", PCSX2_APP, iso_path])
    time.sleep(1)

def delete_game(game, iso_path):
    _, title, _, _, _, _, _ = game
    size = os.path.getsize(iso_path) / (1024 ** 3)
    print(f"\n{R}Delete '{title}' ({size:.1f} GB)?{RS}")
    confirm = input("  Type 'yes' to confirm: ").strip().lower()
    if confirm == "yes":
        os.remove(iso_path)
        print(f"{G}Deleted.{RS}")
    else:
        print("Cancelled.")
    input("\nPress Enter to continue...")

# ─── Menu ──────────────────────────────────────────────────────────────────────

def print_menu(iso_map):
    clear()
    print(f"\n{BD}{C}╔══════════════════════════════════════════════════════════════════════╗{RS}")
    print(f"{BD}{C}║           PS2 GAME MANAGER  ·  PCSX2 Emulator Library               ║{RS}")
    print(f"{BD}{C}╚══════════════════════════════════════════════════════════════════════╝{RS}")
    print(f"  {DM}+N download/launch  ·  -N delete  ·  0 quit  ·  Disk free: {disk_free()}{RS}\n")

    print(f"  {BD}{'#':>3}  {'TITLE':<42} {'YR':>4}  {'GENRE':<17} RATING  STATUS{RS}")
    print(f"  {'─' * 90}")

    for rank, title, year, genre, rating, _, keywords in GAMES:
        iso = find_iso(keywords, iso_map)
        if iso:
            status = f"{G}✓ Downloaded{RS}"
            disp   = f"{BD}{title}{RS}"
        else:
            status = f"{DM}  Available{RS}"
            disp   = title

        print(
            f"  {BD}{rank:>3}{RS}  {disp:<42} {DM}{year}{RS}  "
            f"{genre:<17} {stars(rating)}  {status}"
        )

    print(f"  {'─' * 90}\n")

# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(GAMES_DIR, exist_ok=True)

    while True:
        iso_map = get_iso_files()
        print_menu(iso_map)

        try:
            raw = input(f"  {BD}Enter number: {RS}").strip()
            if not raw:
                continue
            num = int(raw)
        except ValueError:
            print(f"{R}Please enter a number (e.g. 5 to download, -5 to delete, 0 to quit){RS}")
            time.sleep(1.5)
            continue
        except KeyboardInterrupt:
            print(f"\n\n{C}Goodbye!{RS}\n")
            break

        if num == 0:
            print(f"\n{C}Goodbye!{RS}\n")
            break

        if not (1 <= abs(num) <= 50):
            print(f"{R}Enter 1-50 (download), -1 to -50 (delete), or 0 (quit).{RS}")
            time.sleep(1.5)
            continue

        game = GAMES[abs(num) - 1]
        iso  = find_iso(game[6], iso_map)

        if num > 0:
            if iso:
                print(f"\n{G}'{game[1]}' is already downloaded.{RS}")
                print(f"  {DM}{iso}{RS}")
                ans = input(f"\n  {BD}Launch in PCSX2? (y/n): {RS}").strip().lower()
                if ans == "y":
                    launch_game(iso, game[1])
            else:
                download_game(game)
        else:  # num < 0 → delete
            if iso:
                delete_game(game, iso)
            else:
                print(f"\n{Y}'{game[1]}' is not downloaded.{RS}")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
