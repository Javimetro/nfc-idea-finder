# Running Tapwise (NFC Idea Finder)

## On the Raspberry Pi (hwpi), with Docker

From your laptop (PowerShell), copy the project to the Pi:

    scp -r nfc-idea-finder javi@PI-LOCAL-IP:~/

Then on the Pi (`ssh javi@PI-LOCAL-IP`):

    cd ~/nfc-idea-finder
    docker build -t tapwise .
    docker run -d --name tapwise --restart unless-stopped -p 8080:8000 -v tapwise_data:/srv/app/data tapwise

Open in your laptop's browser:

- at home: http://PI-LOCAL-IP:8080
- anywhere (Tailscale): http://PI-TAILSCALE-IP:8080

## After changing ideas or code

    cd ~/nfc-idea-finder
    python3 scripts/build_db.py        # only if you edited build_db.py
    docker build -t tapwise . && docker rm -f tapwise
    docker run -d --name tapwise --restart unless-stopped -p 8080:8000 -v tapwise_data:/srv/app/data tapwise

Visitor suggestions are kept in the `tapwise_data` volume, so rebuilding never deletes them.
See them at http://PI-LOCAL-IP:8080/api/suggestions

## On any computer, without Docker

    pip install flask
    python app/app.py                  # -> http://localhost:8000
