import time

# Dictator praises to cycle through
praises = [
    "All hail Kylian Mbappe, Sovereign of the Semi-Finals!",
    "All hail our supreme dictator of the pitch!",
    "Bow down to the Golden Boot leader!",
    "Long live the absolute ruler of Les Bleus!",
]

try:
    while True:
        for praise in praises:
            # \033[H moves cursor to top-left, \033[J clears down from there
            print("\033[H\033[J", end="")
            print(praise, flush=True)
            time.sleep(1.5)  # Pause so you can read the decree

except KeyboardInterrupt:
    # Allows you to exit safely by pressing Ctrl+C
    print("\033[H\033[J", end="")
    print("Propaganda machine terminated by the resistance.")