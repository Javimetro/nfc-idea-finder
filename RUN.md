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

    ~/projects/nfc-idea-finder/scripts/deploy.sh

It pulls, rebuilds and restarts the container, then checks the site answers. Claude runs it itself after
each change. It reads the secrets from `~/tapwise.env` (outside the repo, never committed), created once:

    printf 'ADMIN_PASSWORD=pick-a-password\nANTHROPIC_API_KEY=sk-ant-...\n' > ~/tapwise.env
    chmod 600 ~/tapwise.env

Visitor ideas, approved community ideas and "I use this" counts are kept in the `tapwise_data` volume,
so rebuilding never deletes them.

**Admin page** (approve ideas into the bank): http://PI-LOCAL-IP:8080/admin
The browser asks for a login: any username, and the password you put in `ADMIN_PASSWORD`.
No `ADMIN_PASSWORD` = the admin page is switched off.

**AI review** (optional): with `ANTHROPIC_API_KEY` set, every new visitor idea gets one Claude call and the AI
decides by itself: new ideas go straight into the bank, duplicates and spam are filed away. `/admin` lists every
decision with an Undo button. Without the key, ideas wait on `/admin` for a human.
Jev (TypeSafe) as the decision maker: add `TYPESAFE_API_KEY=...` and `TAPWISE_REVIEWER=hybrid` to `~/tapwise.env`.
Jev then decides (spam / duplicate / needs) and Claude only writes the text of new ideas. Compare the two first with
`docker exec -i -w /srv/app tapwise python - < scripts/compare_reviewers.py`.
Optional extras: `-e TAPWISE_AI_MODEL=...` (default `claude-opus-5`) and `-e TAPWISE_AI_DAILY_LIMIT=50`
(max AI reviews per day, so a flood of spam can't run up the bill).

## On any computer, without Docker

    pip install -r requirements.txt     # or just `pip install flask` (AI review then stays off)
    python app/app.py                  # -> http://localhost:8000
