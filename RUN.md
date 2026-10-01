# Running Tapwise (NFC Idea Finder)

## On the Raspberry Pi (hwpi), with Docker

### First time (once)

1. The Pi is logged in to GitHub with the GitHub CLI (`gh auth login` + `gh auth setup-git`),
   so it can pull and push over HTTPS. All projects live in `~/projects`
   (the whole Pi setup is explained in `~/projects/SETUP.md`).

2. Download the project:

       git clone https://github.com/Javimetro/nfc-idea-finder.git ~/projects/nfc-idea-finder
       cd ~/projects/nfc-idea-finder

3. Build and start:

       docker build -t tapwise .
       docker rm -f tapwise
       docker run -d --name tapwise --restart unless-stopped \
         -p 8080:8000 \
         -v tapwise_data:/srv/app/data \
         -e ADMIN_PASSWORD='pick-a-password' \
         -e ANTHROPIC_API_KEY='sk-ant-...' \
         tapwise

Open in your laptop's browser:

- at home: http://PI-LOCAL-IP:8080
- anywhere (Tailscale): http://PI-TAILSCALE-IP:8080

### Every update after that

    cd ~/projects/nfc-idea-finder
    git pull
    docker build -t tapwise .
    docker rm -f tapwise
    docker run -d --name tapwise --restart unless-stopped \
      -p 8080:8000 \
      -v tapwise_data:/srv/app/data \
      -e ADMIN_PASSWORD='pick-a-password' \
      -e ANTHROPIC_API_KEY='sk-ant-...' \
      tapwise

Visitor ideas, approved community ideas and "I use this" counts are kept in the `tapwise_data` volume,
so rebuilding never deletes them.

**Admin page** (approve ideas into the bank): http://PI-LOCAL-IP:8080/admin
The browser asks for a login: any username, and the password you put in `ADMIN_PASSWORD`.
No `ADMIN_PASSWORD` = the admin page is switched off.

**AI first review** (optional): with `ANTHROPIC_API_KEY` set, every new visitor idea gets one Claude call that
spots duplicates and spam (filed automatically when it's sure, with an Undo button on `/admin`) and pre-fills the
approve form for new ideas. Without the key everything still works; you just review by hand.
Optional extras: `-e TAPWISE_AI_MODEL=...` (default `claude-opus-5`) and `-e TAPWISE_AI_DAILY_LIMIT=50`
(max AI reviews per day, so a flood of spam can't run up the bill).

## On any computer, without Docker

    pip install -r requirements.txt     # or just `pip install flask` (AI review then stays off)
    python app/app.py                  # -> http://localhost:8000
