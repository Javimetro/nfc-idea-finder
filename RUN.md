# Running Tapwise (NFC Idea Finder)

## On the Raspberry Pi (hwpi), with Docker

### First time (once)

1. Give the Pi a read-only key for this private repo:

       sudo apt install -y git
       ssh-keygen -t ed25519 -C "hwpi" -f ~/.ssh/github_nfc -N ""
       cat ~/.ssh/github_nfc.pub

   Copy the line it prints. On GitHub: repo **Settings → Deploy keys → Add deploy key**,
   paste it, leave "Allow write access" OFF, save.

2. Tell the Pi to use that key for GitHub, then download the project:

       printf 'Host github.com\n  IdentityFile ~/.ssh/github_nfc\n' >> ~/.ssh/config
       git clone git@github.com:Javimetro/nfc-idea-finder.git
       cd nfc-idea-finder

3. Build and start:

       docker build -t tapwise .
       docker rm -f tapwise
       docker run -d --name tapwise --restart unless-stopped \
         -p 8080:8000 \
         -v tapwise_data:/srv/app/data \
         tapwise

Open in your laptop's browser:

- at home: http://PI-LOCAL-IP:8080
- anywhere (Tailscale): http://PI-TAILSCALE-IP:8080

### Every update after that

    cd ~/nfc-idea-finder
    git pull
    docker build -t tapwise .
    docker rm -f tapwise
    docker run -d --name tapwise --restart unless-stopped \
      -p 8080:8000 \
      -v tapwise_data:/srv/app/data \
      tapwise

Visitor suggestions are kept in the `tapwise_data` volume, so rebuilding never deletes them.
See them at http://PI-LOCAL-IP:8080/api/suggestions

## On any computer, without Docker

    pip install flask
    python app/app.py                  # -> http://localhost:8000
