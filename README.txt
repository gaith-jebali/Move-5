MOVE 5 MULTI MATCH

RUN
1. Install Python 3 and the QR package once: pip install qrcode[pil]
2. Keep the computer and all phones on the same Wi-Fi.
3. Run: python server.py
4. On the host computer open: http://localhost:8000
5. Select MULTI MATCH, then HOST A MATCH.
6. Players scan the displayed QR, enter nicknames, and wait.
7. Press START COMPETITION. Everyone gets the same movement and countdown.
8. Players complete the target and press FINISH. The Python server records finish order.

SOLO MODE
Players count their own repetitions and press FINISH CHALLENGE immediately when done. There is no rep button.

IMPORTANT
- This local version needs the Python server; opening index.html directly will not run Multi Match.
- The server is the authority for finish times, reducing phone-clock differences.
- For a public internet version later, deploy the same concept to Render, Railway, Fly.io, or a serverless database. Static GitHub Pages alone cannot host the live match server.

SOUND
- Sound is enabled by default after the first user tap.
- Includes button clicks, roulette ticks, countdown beeps, finish sound, winner fanfare, and vibration when supported.
- Browsers block sound before user interaction; pressing Start/Join unlocks it.
