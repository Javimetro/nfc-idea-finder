"""Builds the first version of the NFC Idea Finder database from the
NotebookLM extraction batches (2026-09-26).

Output (in ./db/):
  sources.json       one row per unique source (duplicates 3, 5, 20 removed)
  ideas.json         one row per canonical idea (duplicates across sources merged)
  idea_sources.json  links idea <-> source, with anchor quote for finding the timestamp later
"""
import json, os

os.makedirs("db", exist_ok=True)

# ---------------------------------------------------------------- sources
S = [
    (1, "10 NEW ADVANCED WAYS to USE NFC Tags For Automation Ideas", "video", "YouTube", "Automated Tech", "en"),
    (2, "3 Crazy NFC Tag Ideas That Show How POWERFUL They Are!", "video", "YouTube", "Tom's Smart Home", "en"),
    (4, "3D Printing with NFC Tags | My Top 6 Prints and How to Make Them Work", "video", "YouTube", "The Scrappy Creative", "en"),
    (6, "5 Creative Uses for NFC Tags & Your iPhone!", "video", "YouTube", "AppleInsider", "en"),
    (7, "Custom NFC Tap Pens - Creative Ideas How to Effectively Use Them For Your Business or Organization", "video", "YouTube", "Perfect Imprints Creative Marketing", "en"),
    (8, "Different Types of Useful NFC Tags!", "video", "YouTube", "Bren Maartens", "en"),
    (9, "Extremely Useful NFC Home Automation Ideas!", "video", "YouTube", "Smart Home Solver", "en"),
    (10, "How I used these NFC tags to organize my whole house?", "video", "YouTube", "Andilynn's Amazing Reviews", "en"),
    (11, "How to Add Door Access Cards to iPhone (Use NFC to Open Doors)", "video", "YouTube", "Digibase Media", "en"),
    (12, "How to Set Up NFC Tags with NFC Tools, Home Assistant & iPhone Shortcuts (Step-by-Step)", "video", "YouTube", "tes io", "en"),
    (13, "How to use NFC Tags in 6 CREATIVE Ways", "video", "YouTube", "PixelGRID", "en"),
    (14, "How you can use NFC to improve your everyday life!", "video", "YouTube", "Caddac", "en"),
    (15, "More NFC content because I love yall. The easy to do vs. usefullness factor here if very high", "video", "YouTube", "Brett Tech", "en"),
    (16, "NFC Stickers #shorts #adhd #nfc", "video", "YouTube", "Olivia Lutfallah", "en"),
    (17, "NFC Stickers streamline your life! Get yours today!", "video", "YouTube", "Nexvolt", "en"),
    (18, "NFC For Dummies (Mueller & Sabella, Wiley, 2016, ISBN 9781119182924)", "book", None, "Robert P. Sabella and John Paul Mueller", "en"),
    (19, "Qué se Puede Hacer con una Tarjeta o Etiqueta NFC en una Casa", "video", "YouTube", "PLUYU", "es"),
    (21, "Stickers NFC: todo lo que puedes hacer con ellos", "video", "YouTube", "Binata", "es"),
    (22, "This is why you NEED NFC Tags! (NFC Tasks Automation)", "video", "YouTube", "Bren Maartens", "en"),
    (23, "Top 5 NFC tag creative ideas", "video", "YouTube", "Slay Tag", "en"),
    (24, "how I use NFC tags around my apartment (the ones that actually stuck)", "video", "YouTube", "Caitlin's Corner", "en"),
    # added in batch 6 (2026-09-26 evening)
    (25, "15 NEW Shortcuts YOU Requested - Alarms, NFC Tags, Photos & More!", "video", "YouTube", "Stephen Robles", "en"),
    (26, "Near Field Communication (NFC) for Embedded Applications (Agus Kurniawan, PE Press, 2015)", "book", None, "Agus Kurniawan", "en"),
]
sources = [{
    "id": f"s{n:02d}", "notebooklm_no": n, "title": t, "url": None, "type": ty,
    "platform": p, "creator_name": c, "creator_url": None, "language": l,
    "published_date": None, "date_added": "2026-09-26",
    "notes": ("Published 2016: phone-compatibility details may be outdated. "
              "Cite the book (publisher/store page), never the file it was read from.") if n == 18 else
             ("Published 2015, maker/embedded book. Cite the book itself, never the file it was read from.") if n == 26 else None,
} for n, t, ty, p, c, l in S]

# ---------------------------------------------------------------- ideas
# kind: diy = visitor can do it with a tag + phone
#       business = a business uses it with customers / sells it
#       industry_example = real-world deployment, not DIY (inspiration only)
#       product_feature = NFC built into a device (no tag to buy)
#       tip = general advice, not a standalone idea
#       maker = build-your-own project with an NFC reader (Raspberry Pi / Arduino)
STD = dict(form="sticker", on_metal=False, waterproof=False, rewritable=True, secure=False, memory="small")
def tag(**kw): return {**STD, **kw}
SHORTCUT = "iPhone: Shortcuts app. Android: NFC Tools Pro, MacroDroid or Tasker."
HA = "Home Assistant (companion app on iPhone or Android)."

ideas, links = [], []
def idea(id, title, summary, how, links_, kind="diy", audience=("personal",), settings=("home",),
         goals=("automation",), phone="any", setup=None, difficulty="easy", cost="under_5_eur",
         tag_needs="DEFAULT", business=None, flags=None):
    ideas.append({
        "id": id, "title": title, "kind": kind, "summary": summary, "how_it_works": how,
        "audience": list(audience), "settings": list(settings), "goals": list(goals),
        "phone_support": phone, "setup_by_platform": setup, "difficulty": difficulty,
        "cost_level": cost, "tag_needs": tag() if tag_needs == "DEFAULT" else tag_needs,
        "business_model": (business or {}).get("model"), "who_pays": (business or {}).get("who"),
        "startup_cost_level": (business or {}).get("cost"), "review_flags": flags or [],
    })
    for src, quote in links_:
        links.append({"idea_id": id, "source_id": f"s{src:02d}", "start_seconds": None,
                      "end_seconds": None, "anchor_quote": quote})

# --- Home & daily life -------------------------------------------------------
idea("i001", "Send music to the speaker in the room",
     "Tap a tag next to a speaker and whatever is playing on your phone moves to that speaker.",
     "Tag near the speaker triggers a smart home automation that switches Spotify playback to it.",
     [(1, "pass off the music you can make the music currently playing on your phone switch to a Spotify source"),
      (9, "switch the spotify source to the echo dot right in the room and automatically start playing")],
     setup=HA, difficulty="medium")
idea("i002", "Keep the garage lights on while you work",
     "Stops motion-sensor lights switching off while you are busy at the workbench.",
     "Tap sets an 'override' switch in your smart home, so the auto-off rule is skipped until you tap again.",
     [(1, "the lights in the garage will remain lit if an NFC tag that is located on your workbench is scanned"),
      (9, "nfc tag in here that will override those lights turning off")],
     setup=HA, difficulty="medium")
idea("i003", "See what is inside a box without opening it",
     "Tap a storage box or moving box to see its contents on your phone.",
     "Three ways: write a text list straight onto the tag; link the tag to a photo album of the contents; or have your smart home send a notification listing them.",
     [(1, "if each container has an NFC tag you can quickly create a list of what is stored in that bin"),
      (1, "attach an NFC tag to the outside of each box so that you can keep track of what's inside"),
      (9, "put an nfc tag that will scan it and it will give me a notification of what's inside"),
      (10, "hold your phone in front of the NFD tag... open the URL all you have to do is click that to open that you can see everything inside"),
      (14, "store text on these and it is extremely helpful for labeling boxes and storage containers")],
     audience=("personal", "workplace"), settings=("home", "warehouse", "office"), goals=("tracking", "share_info"),
     setup="Text list or photo-album link: NFC Tools (any phone). Notification: Home Assistant.",
     tag_needs=tag(memory="medium"),
     flags=["Same concept as the user's 'peek behind' seed idea: link these together."])
idea("i004", "Reset a chore or maintenance reminder",
     "Get reminded to empty the robot vacuum tank, service an appliance or do a chore, and tap the tag when it is done to reset the reminder.",
     "Your smart home keeps a counter or 'last done' date; the tap resets it and clears the notification.",
     [(1, "you can keep tabs on any and all of your errands"),
      (2, "automating appliance maintenance schedules"),
      (9, "scan the nfc tag and it will reset that reminder for another week")],
     goals=("reminder", "tracking", "automation"), setup=HA, difficulty="medium",
     flags=["Tags on metal appliances need anti-metal (on-metal) tags."])
idea("i005", "Pause doorbell alerts while you work outside",
     "Stops your video doorbell sending motion alerts while you garden or clean near the door.",
     "Tap toggles a switch that mutes the doorbell notifications; tap again to turn them back on.",
     [(1, "doorbell motion alerts are temporarily suspended whenever it is scanned"),
      (9, "nfc tag right here in the light switch plate next to the front door... disable them all")],
     setup=HA, difficulty="medium")
idea("i006", "One-tap timer where you need it",
     "Start the right timer with one tap: kettle, oven, laundry, baby milk bottle, toothbrushing, car parking.",
     "Each tag starts a preset timer (e.g. 5 min kettle, 2 min toothbrush, 2 h baby bottle, 1.5 h parking). Laundry version: tap again to cancel.",
     [(1, "add a tag that will start the timer for you instead of having to do it yourself"),
      (15, "five minute timer that I have next to my Kettle... tap this with my phone and will set a five minute timer"),
      (15, "tap it to the tag and will set a two minute timer so I make sure I brush my teeth long enough"),
      (4, "bottle timer So for those of you with kids you know that milk can only be out so long"),
      (9, "scan the tag again and it will cancel out the timer"),
      (22, "in my car I have a tag that when tapped set a timer for that exact time as I get out")],
     settings=("home", "car"), goals=("reminder", "automation"), setup=SHORTCUT)
idea("i007", "Unlock a smart door lock with a tap",
     "Tap your phone on a tag by the door to unlock a smart lock.",
     "Tag triggers the unlock action of your smart lock app or smart home.",
     [(1, "install an NFC tag on it to make it automatically unlock when you approach it")],
     goals=("access", "automation", "security"), setup=HA,
     flags=["Security: never write an unlock URL onto the tag itself (anyone could scan it). Use a phone automation that reacts to the tag, and keep the phone locked-screen protection on. See i030."])
idea("i008", "Leaving-home routine",
     "One tap by the door as you leave: lights off, heating/AC to away, alarm armed, robot vacuum starts, transit app opens.",
     "Tag by the exit runs a multi-step routine in your smart home or phone automation app.",
     [(1, "simply tap your phone to turn off the heating or cooling system"),
      (1, "tag will turn off all the lights for you at the same time"),
      (9, "nfc sticker right next to your door... arms your alarm put your thermostats in away mode start your robot vacuum"),
      (14, "tag by your front door so that on your way out you give it a tap it turns off any lights"),
      (24, "puts my house in lockdown mode... open up the TTC app so I can see if there's any delays"),
      (19, "al pasar el teléfono delante del tag nfc se va a activar la escena")],
     goals=("automation", "security"), setup=f"{HA} Or: {SHORTCUT}")
idea("i009", "Arriving-home routine",
     "Tap when you get home (or from the car on the way) to switch on lights, connect to wifi, set the phone to quiet and bring the heating/cooling back.",
     "Tag at the entrance or in the car runs an 'I'm home' routine.",
     [(22, "put your phone onto vibrate connect to your home Wi-Fi and then open up your home automation app to automatically turn the lights on"),
      (9, "scan on my phone and that will send all my thermostats back into cooling mode")],
     settings=("home", "car"), setup=f"{SHORTCUT} Smart home app for lights/heating.")
idea("i010", "Bedtime routine",
     "Tap the nightstand (or put the phone on its charger) to turn off every light, switch on a dim bedside lamp and enable sleep / do-not-disturb mode.",
     "Tag on the nightstand or stuck to the wireless charger runs your bedtime routine.",
     [(9, "scan it at night when she goes to bed and it turns off every single light in the house"),
      (24, "turns off all of the lights in my apartment but it also turns on the lamp in my bedroom"),
      (14, "wireless charging by your bedside you can have an NFC sticker on there... enabling sleep mode"),
      (19, "Apagar todas las luces inteligentes desde un tag nfc para esto vamos a usar una función gratuita... virtual"),
      (25, "run my smart home good night scene to turn off all the lights")],
     setup=f"{SHORTCUT} Smart lights app or Home Assistant.",
     flags=["Charger version: check the tag does not interfere with wireless charging."])
idea("i011", "One tag, different action depending on the time",
     "The same nightstand tag turns on hallway lights at 1 AM but starts your morning routine at 7 AM.",
     "The automation checks the clock when the tag is tapped and picks the matching routine.",
     [(9, "different functionality depending on what time of day it is")],
     setup=HA, difficulty="medium")
idea("i012", "Kids' bedtime from the light switch",
     "A tag on the child's light switch dims the lights and starts lullabies.",
     "Parent taps the tag; routine dims lights and plays music on a smart speaker. Kids can't fiddle with it like a button.",
     [(9, "trigger a bedtime routine with it so it will dim the lights and start playing lullabies")],
     setup=HA)
idea("i013", "Tap-to-toggle lights (a light switch without wiring)",
     "Stick a tag where you want a light switch and tap to turn lights on or off. Great for renters or hard-to-reach lamps.",
     "Tag triggers a toggle of smart bulbs, plugs or LED strips. Can be hidden in a 3D-printed switch plate.",
     [(4, "This is a smart light switch And how it works is by triggering an iPhone automation"),
      (12, "turning on and off this strip light"),
      (16, "turn my lights on and off"),
      (19, "controlamos nuestras luces del jardín con el Loop domótico Girón y pegamos el enlace")],
     goals=("automation", "accessibility"), setup=f"{SHORTCUT} Or {HA}")
idea("i014", "Movie night mode",
     "Tap a tag hidden behind a painting or next to the TV to dim lights, stop motion sensors, open Netflix or even start the popcorn machine.",
     "Tag runs a 'movie' scene; separate tags can each open a different streaming app.",
     [(9, "hidden in canvas picture... turns off movie mode in this room turns off all the lights and it disables the motion sensors"),
      (14, "stick an NFC sticker behind there... enabling the theater mode in your living room"),
      (17, "start NetFlix one to start HBO and one to set the perfect mood lighting"),
      (17, "popcorn automation which starts a fresh batch of popcorn from the comfort of my couch")],
     setup=f"{SHORTCUT} Or {HA}")
idea("i015", "Play an album by tapping its record cover",
     "Records on the wall become buttons: tap the cover and that album plays on your TV or speakers.",
     "Tag hidden in each album sleeve passes the album ID to a script that turns on the audio gear and starts playback.",
     [(2, "each of those album covers not only has the original record still inside but in the lower lefthand corner there's an NFC tag")],
     setup=HA, difficulty="advanced")
idea("i016", "Start your favourite music with a tap",
     "Tap a tag and a chosen playlist starts on your speaker. With several people at home, the same tag can play each person's own favourites.",
     "Tag runs a phone automation that plays a playlist and sends it to a speaker (AirPlay, HomePod, Sonos). Each family member can set up their own automation for the same tag.",
     [(19, "cada miembro de la familia Puede reproducir automáticamente sus canciones favoritas de sus gustos"),
      (25, "when you scan an NFC tag you can have it start playing music")],
     setup=SHORTCUT)
idea("i017", "Plant care at a tap",
     "Tap a plant pot to see its care instructions, or tap the watering can to log that plants were watered.",
     "Pot tag links to a care sheet (e.g. a Google Doc) or sends a notification; watering-can tag adds a calendar entry.",
     [(2, "each of my pots has an NFC tag on the side that I can scan with my phone and I get a notification sent to me"),
      (4, "planter that has an NFC tag built in to the base"),
      (24, "underneath my watering can... adds an event to my calendar that says plants have been watered")],
     settings=("home", "outdoors"), goals=("share_info", "reminder", "tracking"),
     setup=f"Care-sheet link: NFC Tools (any phone). Logging: {SHORTCUT}",
     tag_needs=tag(waterproof=True))
idea("i018", "Take-out-the-trash reminder you can silence",
     "Your phone nags you on bin day until you tap the tag on the bin outside.",
     "Reminder repeats until the bin tag is scanned, then resets for next week.",
     [(9, "my smart home will remind me over and over again until I actually come out here and then I just scan"),
      (14, "stick these on their garbage bins... make sure that they don't forget to put their garbage bins out")],
     settings=("home", "outdoors"), goals=("reminder", "automation"), setup=HA,
     tag_needs=tag(form="epoxy_disc", waterproof=True))
idea("i019", "Call for help from another room",
     "Out of toilet paper? Tap the bathroom tag and every smart speaker announces you need help.",
     "Tag triggers an announcement on all smart speakers.",
     [(9, "scan that nfc tag and it will announce on all the echoes that you need help")],
     setup="Alexa or Google Home routine via Home Assistant or phone automation.")
idea("i020", "Home manual behind the light switch",
     "A tag hidden behind a switch plate shows how the room's smart home works and which fuse controls it.",
     "Tag links to a documentation page for that room.",
     [(9, "behind the light switch wall plate... documentation for their smart home")],
     audience=("personal", "workplace"), settings=("home", "office"), goals=("share_info",),
     setup="NFC Tools (any phone).")
idea("i021", "Garden watering, shutters and heating at a tap",
     "Start a 30-minute watering cycle, close all shutters or switch heating to comfort mode with a tap.",
     "Tag sends a command to your home automation hub.",
     [(19, "activa el riego del jardín durante 30 minutos Entonces podéis lanzar esta desde un tag nfc"),
      (19, "Cerrar todas las persianas con pasar vuestro teléfono encima de este tag nfc")],
     settings=("home", "outdoors"), setup="Home automation hub (Jeedom, Home Assistant).", difficulty="medium",
     tag_needs=tag(waterproof=True))
idea("i022", "Grocery list at a tap",
     "Tap the fridge to open your shopping list, or tap a jar when it runs out to add that item automatically.",
     "Fridge tag opens a list or grocery-delivery site; tags on food containers each add their item to the list.",
     [(24, "NFC sticker to open up the groceries notes within the reminders app"),
      (14, "NFC tag on the inside of his fridge... launch his grocery shopping website"),
      (15, "tag to pretty much every consumable in my house... adds that item to my shopping list"),
      (16, "add items to a grocery list just by tapping the item"),
      (25, "running the automation which adds it to my reminders")],
     goals=("reminder", "automation"), setup=SHORTCUT)
idea("i023", "Packing list inside your suitcase",
     "Tap the tag in your luggage to get your standard packing checklist.",
     "Tag opens or creates a checklist in your reminders/notes app.",
     [(6, "put a little NFC tag into his luggage and then every time he goes to pack... generate a packing list")],
     settings=("travel", "home"), goals=("reminder",), setup=SHORTCUT)
idea("i024", "Hard-to-ignore alarm clock",
     "Your alarm only stops when you get out of bed and tap a tag across the room (e.g. in the bathroom).",
     "Alarm app with an 'NFC challenge': the tag's ID is the only way to dismiss it.",
     [(13, "touch your phone to the NFC tag to dismiss your alarm"),
      (14, "alarm that can only be turned off by tapping my phone on an NFC tag... Sleep as Android")],
     goals=("reminder",), setup="Android: Sleep as Android or Alarmy. iPhone: Alarmy.",
     flags=["Verify current iPhone app support before publishing."])
idea("i025", "Morning briefing read out loud",
     "Tap a tag in the morning and your phone reads today's calendar to you.",
     "Tag runs an automation that fetches today's events and speaks them.",
     [(16, "have all events in my calendar read in the morning to me")],
     goals=("reminder", "accessibility"), setup=SHORTCUT)
idea("i026", "Pick up and take the next step (ADHD-friendly routines)",
     "Physical tags as reminders and shortcuts reduce the steps between intention and action.",
     "Combine timers (i006), grocery list (i022), morning briefing (i025) and light toggles (i013).",
     [(16, "turn my lights on and off")], kind="tip", goals=("accessibility",),
     flags=["Framing tip for the results page, not a standalone idea. Consider an 'accessibility' interview answer."])

# --- Health & habits ---------------------------------------------------------
idea("i027", "Log a coffee or a glass of water",
     "Tap the coffee machine or your water bottle to log caffeine or water into your health app.",
     "Tag runs an automation that adds a preset amount to Apple Health (or opens your tracking app).",
     [(6, "put an NFC tag on top of my Nespresso maker then every time I go to get a cup of coffee I tap my phone"),
      (23, "scan the NFC tag to log your caffeine intake into the health app"),
      (22, "putting a small tag on the water bottle every time you refill it you tap the tag and it will open up your health app")],
     settings=("home", "office"), goals=("tracking",), setup=SHORTCUT,
     tag_needs=tag(waterproof=True))
idea("i028", "Did I take my pills today?",
     "Tap the pill bottle when you take your medicine or vitamins; your phone records it so you never double-dose.",
     "Tag marks today's reminder as done or logs the time.",
     [(6, "take a look at take the meds in this case I can tap my iPhone on the NFC tag that I've attached to the top of my little medicine bottle"),
      (14, "stickers on the top of one of your medication bottles... marks you as taking your medication")],
     goals=("tracking", "reminder"), setup=SHORTCUT)
idea("i029", "Reorder your medicine",
     "A tag under the pill bottle opens the pharmacy reorder page.",
     "Tag holds the pharmacy's reorder link.",
     [(22, "bottom of a medication bottle so when you tap it it might open up a pharmaceutical company's website that will remind you to re-order")],
     goals=("reminder",), setup="NFC Tools (any phone).")
idea("i030", "Set up the room for your workout",
     "Tap your bike, mat or gear to close blinds, set lights, open your workout video and play the right music.",
     "Tag runs a workout scene: smart home + opens fitness app or video.",
     [(6, "put NFC tag on the cycling equipment... wake up the living room Apple TV... open the fitness app... close the blinds"),
      (15, "put an NFC tag in that spot to trigger my yoga slash relax smart home automation"),
      (21, "si haces ejercicio puedes abrir tu rutina acercando tu celular a un sticker")],
     goals=("automation",), setup=SHORTCUT)

# --- Focus & productivity ----------------------------------------------------
idea("i031", "Focus mode at your desk",
     "Tap a tag in your desk drawer, notebook or e-reader case to silence notifications, start a Pomodoro timer and open your calendar or music.",
     "Tag switches on a Focus / do-not-disturb mode, starts a timer and opens your work tools.",
     [(24, "NFC sticker stuck to the inside of one of my top office drawers... turns on my work focus"),
      (24, "slip behind my e-reader case... program an automation with an NFC tag"),
      (23, "put your phone on do not disturb and set a timer for focused activities"),
      (21, "En tu escritorio puedes poner un sticker y cuando lo acerques abra el calendario o el proyecto")],
     audience=("personal", "workplace"), settings=("office", "home"), goals=("automation",), setup=SHORTCUT)
idea("i032", "Lock distracting apps behind a tag",
     "Social media apps stay locked until you walk to the tag across the flat and tap it.",
     "Screen-time app uses the tag as the physical key to lock/unlock chosen apps.",
     [(24, "creating my own brick... when I want to lock the social media apps on my phone I scan it")],
     goals=("automation",), setup="Focus-blocking app with NFC unlock (check current app options).")
idea("i033", "Save an idea by talking to your phone",
     "Tap your phone on a keychain tag and your phone starts listening. Say your idea and your phone types it into your notes. The tag has no microphone: it just tells your phone to start dictation.",
     "The tag holds nothing but a trigger. Your phone recognises it and runs an automation that starts dictation (your phone's microphone) and saves the text to a note.",
     [(24, "opens up a voice note that I can speak into and it will dictate the text"),
      (12, "voice memo cuz I want to start recording some voices"),
      (23, "Launch diation mode to turn what you say into text")],
     settings=("home", "office", "travel"), goals=("automation", "tracking"), setup=SHORTCUT,
     tag_needs=tag(form="keyfob"))
idea("i034", "Open your journal or planner",
     "A tag in your paper planner opens your digital planning page, music and timer.",
     "Tag opens Notion (or your journal app) plus optional timer and music.",
     [(24, "slipped an NFC tag in one of my pockets here that opens up a journaling planning mode"),
      (23, "gain deeper insight into yourself and increase your personal growth and development with digital journaling")],
     settings=("home", "office"), goals=("automation",), setup=SHORTCUT)
idea("i035", "Open the right app where you use it",
     "Put a tag where an app belongs: toothbrush case opens the toothbrush app, scale opens the weight app, study notebook opens your lesson, kitchen opens food delivery.",
     "Tag launches a specific app or web link.",
     [(14, "tag on the case for my toothbrush I tap my phone on there and it automatically launches the app for the toothbrush"),
      (14, "one on my Smart scale so that I can launch my smart Scale app"),
      (14, "make this one launch dominoes... order myself a pizza"),
      (21, "mi libreta de inglés y le pegué un sticker NFC... abra directamente el contenido que estoy usando para estudiar")],
     setup="Web link: NFC Tools (any phone). Open an app: iPhone Shortcuts / Android NFC Tools.")
idea("i036", "Start your computer and desk lights",
     "Tap your desk to boot your PC and switch on the lights behind it.",
     "Tag triggers wake-on-LAN plus a light scene in your smart home.",
     [(12, "My PC just turned on and my light behind my PC just turned on")],
     audience=("personal", "workplace"), settings=("office", "home"), setup=HA, difficulty="medium")
idea("i037", "Hotspot for your laptop in one tap",
     "Tap the tag on your laptop and your phone turns its hotspot on (or off).",
     "Android automation toggles the hotspot when the tag is read.",
     [(13, "create a Wi-Fi hotspot on the go for your laptop"),
      (22, "put a tag on top of your laptop that when you tap it will turn your mobile hotspot on and off")],
     audience=("personal", "workplace"), settings=("office", "travel"), goals=("automation", "access"),
     phone="android_only", setup="Android: MacroDroid or NFC Tasks.",
     flags=["iPhone cannot switch the hotspot on from an automation; confirm before listing as Android-only."])
idea("i038", "Switch wifi or Bluetooth off to save battery",
     "Tap your desk tag to switch radios you don't need off (or on).",
     "Automation toggles wifi/Bluetooth.",
     [(14, "automatically enables or disables your Bluetooth or your Wi-Fi")],
     settings=("office",), phone="android_only", setup="Android: NFC Tools Pro or MacroDroid.")
idea("i039", "Check your bank balance by SMS",
     "Tap a tag to send your bank's balance-request text message.",
     "Tag sends a preset SMS to your bank's number.",
     [(13, "send SMS by tapping on NFC tag to know your bank balance")],
     setup="Android: MacroDroid.", flags=["Only works with banks that offer SMS balance; niche."])

# --- Car & travel ------------------------------------------------------------
idea("i040", "Driving mode from the car mount",
     "Put your phone in the car mount and Bluetooth, navigation and music start automatically.",
     "Tag stuck in the phone holder or dashboard runs a driving routine.",
     [(13, "turn on Bluetooth put your phone to vibrating mode launch the Google Maps or music"),
      (14, "put your phone into your phone holder in your car it automatically launches your favorite navigation app"),
      (22, "put one in your car that when scan sets your destination automatically turns your music app on and then sends a message")],
     settings=("car",), setup=SHORTCUT)
idea("i041", "Let family know where you are",
     "One tap sends your ETA, location or 'arrived safely' message to someone.",
     "Tag in the car or at the door runs an automation that calculates your ETA or grabs your location and texts it.",
     [(6, "tap the NFC tag right there on the dash... calculate driving time... send a text message"),
      (23, "scan the NFC tag to automatically send her a text with your precise location"),
      (21, "sticker pegado en la puerta de mi casa... cuando yo llego... envía un mensaje")],
     settings=("car", "home", "travel"), goals=("share_info", "automation"), setup=SHORTCUT)
idea("i042", "Open the garage or gate from the car",
     "Tap a tag behind the sun visor to open the garage door or the driveway gate.",
     "Phone automation reacts to the tag and calls the garage/gate system (or dials the gate's phone number).",
     [(9, "little nfc sticker right behind my visor and if I'm heading home I can just scan that and that will open up my garage door"),
      (19, "permitir abrir el portón eléctrico de vuestra casa pero solamente desde vuestro teléfono"),
      (22, "instead of phoning it you can actually just add the phone number to a tag and then tap your phone against that tag")],
     settings=("car", "home"), goals=("access", "automation", "security"),
     setup=f"{SHORTCUT} Plus a smart garage/gate controller.", difficulty="medium",
     flags=["Security pattern (from PLUYU): tag holds nothing; only YOUR phone's automation reacts to it."])

# --- Sharing & contact -------------------------------------------------------
idea("i043", "Guest wifi with one tap",
     "Guests tap a coaster or sticker and connect to your wifi without typing the password. Works at home, in cafes and salons.",
     "Wifi name and password are written onto the tag as a wifi record.",
     [(4, "statue and the coasters have NFC chips in them with my Wi-Fi credentials"),
      (13, "give Wi-Fi access to your guests with just one tap"),
      (14, "write it directly to the tag... Wi-Fi network"),
      (21, "pones uno de estos stickers en tu salón de belleza... se conecten al Wi-Fi")],
     audience=("personal", "business_customers"), settings=("home", "shop", "restaurant", "office"),
     goals=("share_info", "access"), phone="android_only", setup="Write with NFC Tools or InstaWifi.",
     tag_needs=tag(memory="medium"),
     flags=["Android joins automatically; iPhones generally don't join wifi from a tag record. Verify current iOS behaviour and suggest a QR code fallback."])
idea("i044", "Smart business card",
     "Tap your card, keychain or sticker to share your contact, website, portfolio or social profiles.",
     "Tag holds a contact card (vCard) or a link to your portfolio / link page. Can be embedded in a 3D print or stuck on an old plastic card.",
     [(4, "3D printed gifts video And this is a smart business card"),
      (12, "program an NFC tag using your phone to store your contact information"),
      (13, "share all your contact info with just one tap"),
      (14, "stick a NFC sticker onto the back of a business card and have people scan it"),
      (21, "llavero... puse el sticker NFC... acercar el celular al llavero y automáticamente les abre mis redes sociales"),
      (21, "reutilizar una tarjeta que ya no servía... pegando el sticker al centro"),
      (21, "si eres diseñador... podrías tener una tarjeta de estas... y que lleve a tu portafolio"),
      (22, "In my previous video I showed you how to make a smart business card")],
     audience=("personal", "workplace", "nfc_as_business"), settings=("office", "events"),
     goals=("share_info", "marketing"), setup="NFC Tools (any phone).",
     tag_needs=tag(form="card", memory="medium"),
     business={"model": "one_time_sale", "who": "professionals, freelancers, small businesses", "cost": "low"},
     flags=["A link is more flexible than a vCard: you can change it later without rewriting the card."])
idea("i045", "Your saved links behind a picture",
     "A tag behind a small painting opens a note with all your social links, ready to copy.",
     "Tag opens a specific note on your phone.",
     [(24, "mini painting... behind it I have an NFC tag... opens up my notes that has my social media links")],
     audience=("personal", "workplace"), goals=("share_info",), setup=SHORTCUT)
idea("i046", "Lost & found tag for kids, pets and belongings",
     "Whoever finds a lost pet, child or bag can tap the tag and see how to contact you.",
     "Tag on a collar, hat or bag links to a page with your contact details (and pet info).",
     [(18, "Tappy NFC hat... someone just needs to tap the child's hat to discover how to contact you"),
      (18, "Anyone can read the chip using an NFC-enabled device... PetHub")],
     settings=("pets", "outdoors", "travel"), goals=("share_info", "security"), setup="NFC Tools (any phone).",
     tag_needs=tag(form="epoxy_disc", waterproof=True),
     flags=["Privacy: link to a page you control and can edit, not your raw phone number. Examples in the book are from 2016."])
idea("i047", "A gift that plays a message",
     "Jewellery, a keepsake or a 3D print that opens a voice message, photo or video when tapped.",
     "Tag inside the object links to a private media page.",
     [(18, "artistic pearl called Momento... contains an NFC chip that you can encode with a message")],
     audience=("personal", "nfc_as_business"), settings=("home", "events"), goals=("share_info",),
     setup="NFC Tools (any phone).", tag_needs=tag(form="epoxy_disc"),
     business={"model": "custom_product", "who": "gift buyers", "cost": "medium"})
idea("i048", "Hidden secret note in an object",
     "A tag inside a desk organiser holds a text you can only read with an NFC reader app.",
     "Text is written onto the tag; reading it requires opening an NFC app.",
     [(4, "store sensitive information in a little bit of a more discreet way")],
     audience=("personal",), settings=("home", "office"), goals=("share_info",), setup="NFC Tools.",
     flags=["DO NOT recommend for passwords or crypto keys: any phone with a free NFC app can read the tag. Rephrase as a hidden message / fun secret, or drop."])

# --- Business with customers -------------------------------------------------
idea("i049", "Tap to leave a review",
     "Customers tap a sticker on the packaging, counter or table and land directly on your review page.",
     "Tag holds the link to your Google (or other) review page, with a small 'tap to review' sign.",
     [(21, "Acerca tu celular para dejarnos una reseña... debajo de este sticker está el otro sticker NFC")],
     kind="business", audience=("business_customers", "nfc_as_business"), settings=("shop", "restaurant"),
     goals=("marketing",), setup="NFC Tools (any phone).",
     business={"model": "subscription_or_lease", "who": "cafes, salons, shops, e-commerce brands", "cost": "low"},
     flags=["Directly related to the user's NFC review-cards leasing idea."])
idea("i050", "Digital menu on the table",
     "Guests tap a table sticker or coaster to open the menu on their phone.",
     "Tag links to an online menu; update the menu without reprinting.",
     [(21, "pegar uno de estos stickers en la mesa o en un portavasos... les abra el menú")],
     kind="business", audience=("business_customers", "nfc_as_business"), settings=("restaurant",),
     goals=("share_info",), tag_needs=tag(form="epoxy_disc", waterproof=True),
     business={"model": "subscription_or_lease", "who": "restaurants and cafes", "cost": "low"})
idea("i051", "Product info inside the packaging",
     "Customers tap the lid or label to see instructions, ingredients or care tips.",
     "Tag on the product links to an info page you can update.",
     [(21, "esta vela y este sticker lo puedes pegar en la tapa... leer las instrucciones de uso")],
     kind="business", audience=("business_customers",), settings=("shop",), goals=("share_info", "marketing"),
     flags=["Matches the 'product ingredients' application of the user's 'peek behind' seed idea."])
idea("i052", "Follow us / visit our website sign",
     "A small sign on a market stall, counter or window: tap to follow on social media or open the website.",
     "Tag behind a printed sign links to a profile or site.",
     [(21, "crear un letrero pequeño en tu mesa que diga... acerca a tu celular para seguirnos en redes"),
      (14, "if you're a small business owner you can have it launch your website")],
     kind="business", audience=("business_customers", "nfc_as_business"), settings=("shop", "events"),
     goals=("marketing",), business={"model": "one_time_sale", "who": "market vendors, small shops", "cost": "low"})
idea("i053", "Smart posters and print ads",
     "Posters, flyers or magazine ads with a tap spot that opens a video, coupon or event page.",
     "Tags behind the print link to campaign content.",
     [(18, "SmartPosters can appear in all sorts of places, such as bus shelters, malls, and airports"),
      (18, "place your phone on the magazine to test-drive the Lexus Enform App Suite")],
     kind="business", audience=("business_customers", "nfc_as_business"), settings=("shop", "events", "travel"),
     goals=("marketing",), business={"model": "custom_product", "who": "advertisers, venues, event organisers", "cost": "low"},
     flags=["2016 examples; look for a recent source too."])
idea("i054", "Branded NFC promo items (pens, merch)",
     "Promotional pens or merch that open a demo video, booking page or product launch page when tapped.",
     "NFC chip in the item links to a page you keep updating (teaser -> launch -> follow-up).",
     [(7, "at a trade show for instance... send someone straight to a landing page with demo videos"),
      (7, "guide customers from a teaser content in the beginning to launch day details... just by updating the web page")],
     kind="business", audience=("workplace", "business_customers", "nfc_as_business"), settings=("events", "office"),
     goals=("marketing",), cost="5_to_50_eur", tag_needs=tag(form="epoxy_disc", rewritable=False),
     business={"model": "custom_product", "who": "companies at trade shows, product launches", "cost": "low"},
     flags=["Source is a seller of NFC pens: commercial bias."])
idea("i055", "Interactive restaurant tables for kids",
     "Tags under the table turn it into a game board kids play with a phone while waiting for food.",
     "Several tags under the table trigger actions in a game app.",
     [(18, "Happy Table actually looks like a whole lot of fun... turning a static piece of furniture (a table) into an interactive digital experience")],
     kind="business", audience=("business_customers",), settings=("restaurant",), goals=("marketing",),
     difficulty="advanced", cost="5_to_50_eur",
     business={"model": "custom_product", "who": "family restaurants", "cost": "medium"},
     flags=["Needs a custom app; 2016 example."])
idea("i056", "For-sale sign with listing info",
     "Passers-by tap the estate agent's yard sign to see the listing.",
     "Tag on the sign links to the property page.",
     [(18, "use NFC on For Sale yard signs so that prospective buyers can quickly and easily get the information")],
     kind="business", audience=("workplace", "business_customers"), settings=("outdoors",), goals=("marketing", "share_info"),
     tag_needs=tag(waterproof=True))

# --- Workplace ---------------------------------------------------------------
idea("i057", "Guard patrol checkpoints",
     "Guards tap tags along their route to prove each checkpoint was visited, with time stamps.",
     "Patrol app logs each tag scan; missed checkpoints raise an alert.",
     [(18, "guards can log in to show that they actually did make their required rounds by tapping tags")],
     audience=("workplace", "nfc_as_business"), settings=("office", "warehouse"), goals=("tracking", "security"),
     difficulty="medium", tag_needs=tag(on_metal=True, waterproof=True, secure=True),
     business={"model": "service", "who": "security companies, facility managers", "cost": "medium"})
idea("i058", "Cleaning rounds and supply reordering",
     "Cleaners tap tags to confirm a room was cleaned, check equipment in and out, and reorder supplies.",
     "Each tag = one room, tool or supply; the app logs the tap.",
     [(18, "Workers can tap to check out and check back in equipment used for the day")],
     audience=("workplace", "nfc_as_business"), settings=("office", "warehouse", "shop"), goals=("tracking",),
     difficulty="medium", tag_needs=tag(waterproof=True),
     business={"model": "service", "who": "cleaning companies, facility managers", "cost": "medium"})
idea("i059", "Vehicle inspection checklist",
     "Drivers tap tags on each part of the truck to prove the pre-trip check was done.",
     "Tags placed around the vehicle open the right checklist item in an inspection app.",
     [(18, "adding NFC tags to various locations on a vehicle, a driver can indicate they inspected the area")],
     audience=("workplace",), settings=("car", "warehouse", "outdoors"), goals=("tracking",), difficulty="medium",
     tag_needs=tag(form="epoxy_disc", on_metal=True, waterproof=True))

# --- Industry examples & built-in NFC (inspiration, not DIY) ----------------
for i, (title, summary, quote, settings, goals) in enumerate([
    ("Hospital patient wristbands", "Nurses tap a patient's wristband to pull up records and check medication.", "medical professional can read the wristband with an NFC-enabled tablet... to identify the patient", ("health",), ("tracking", "security")),
    ("Medication verification in hospitals", "Scanning wristband + medicine confirms right patient, right dose.", "scans the patient's NFC tag and uses the medical record obtained to get a list of medications", ("health",), ("tracking", "security")),
    ("Anti-counterfeit medicine packaging", "Tap a medicine box to check it is genuine and see instructions.", "tap the tag on a medication bottle and learn more about it on your NFC-enabled smartphone", ("health", "shop"), ("security", "share_info")),
    ("Cold-chain temperature logger", "Shipping tags record temperature; tap to read the history.", "credit card-sized device incorporates LEDs... tells you whether the package has experienced temperatures outside the desired range", ("warehouse",), ("tracking",)),
    ("Transit cards", "Tap card or phone at the gate to pay the fare.", "Oyster card... capability to tap their card to gain access to the required transportation services", ("travel",), ("payments", "access")),
    ("Campus ID on the phone", "Students open doors, pay and borrow books with their phone.", "relying on NFC to provide campus credentials makes sense", ("office",), ("access", "payments")),
    ("Hotel room key on the phone", "Guests unlock their room with their phone.", "hotel can place the key to a room on an NFC-enabled phone", ("travel",), ("access",)),
    ("Phone as car key", "Tap to unlock the car; seat and mirrors adjust to the driver.", "tap your phone against the door... tap a tag to automate tasks such as adjusting your seat position", ("car",), ("access",)),
    ("NFC driving licence", "ID cards with a chip that authorities can read.", "French drivers now have multifunction NFC-enabled driver's licenses", ("car", "travel"), ("security",)),
], start=60):
    idea(f"i{i:03d}", title, summary, "Built by organisations with secure, dedicated systems; shown as inspiration.",
         [(18, quote)], kind="industry_example", audience=("workplace",), settings=settings, goals=goals,
         difficulty="advanced", cost=None, tag_needs=tag(form="card", secure=True),
         flags=["Not DIY. Show only as 'NFC in the real world' inspiration. 2016 examples."])

for i, (title, summary, quote) in enumerate([
    ("Tap to pair a Bluetooth speaker", "Many speakers and headphones pair when you touch your phone to them.", "tap your portable speakers, and the music currently playing on your smartphone starts playing"),
    ("Tap to mirror your phone on a TV", "Some TVs start screen sharing when you touch them with your phone.", "single tap is enough to make a connection with your smartphone so that you can see"),
    ("Tap to print", "Some printers accept a print job when you touch them with your phone.", "simply place your NFC-enabled device against the printer and tell it to send the files"),
    ("Accessible appliances", "Blind users set a microwave from an accessible phone app and tap to send the settings.", "people who are blind may not be able to interact with the touch panel of a microwave... putting the settings into their smartphone"),
    ("Phone-to-phone sharing", "Touch two phones together to share contacts or files.", "tapping your phone with that of a potential client creates the connection that transfers the presentation"),
], start=69):
    idea(f"i{i:03d}", title, summary, "NFC is built into the device; no tag to buy.", [(18, quote)],
         kind="product_feature", goals=("share_info", "automation"), cost=None, tag_needs=None,
         flags=["No tag needed; results page should say 'check if your device supports this'.",
                "Phone-to-phone (Android Beam) was removed from Android in 2019." if "Phone-to-phone" in title else "2016 source; check current devices."])
# i069/i073 also have a second source
links.append({"idea_id": "i069", "source_id": "s22", "start_seconds": None, "end_seconds": None,
              "anchor_quote": "pair your phone with a Bluetooth speaker or even transfer files between two devices"})

# --- Maker projects: build your own NFC reader (Raspberry Pi / Arduino) ------
MAKER = "Reader module (e.g. PN532) on a Raspberry Pi or Arduino, plus a small program. Visitors' phones not needed."
idea("i079", "Tap-in attendance logger",
     "Members tap their card on a reader at the door and the system logs who came and when. Good for clubs, classes, small offices or a coworking space.",
     "A PN532 reader on a Raspberry Pi or Arduino reads each card's ID and a small program matches it to a person and saves the time.",
     [(26, "Register NFC cards to specific person When NFC card is swapped, a program will send data to computer")],
     kind="maker", audience=("workplace", "nfc_as_business"), settings=("office", "events"), goals=("tracking",),
     phone=None, setup=MAKER, difficulty="advanced", cost="5_to_50_eur", tag_needs=tag(form="card"),
     business={"model": "service", "who": "clubs, gyms, schools, coworking spaces", "cost": "low"},
     flags=["NotebookLM listed PN532 as the tag chip; it is the reader module. Cards: MIFARE Classic or NTAG.",
            "Card IDs can be copied: fine for attendance, not for security."])
idea("i080", "Prepaid card for a club kiosk or canteen",
     "Members top up credit and pay at a club kiosk, school canteen or event bar by tapping a card.",
     "A reader on a Raspberry Pi reads the card ID, looks up the balance, subtracts the price and saves the new balance.",
     [(26, "Each NFC card is registered and pointed to a person with deposit amount")],
     kind="maker", audience=("business_customers", "workplace", "nfc_as_business"), settings=("shop", "restaurant", "events"),
     goals=("payments",), phone=None, setup=MAKER, difficulty="advanced", cost="5_to_50_eur", tag_needs=tag(form="card", secure=True),
     business={"model": "service", "who": "clubs, event organisers, small canteens", "cost": "medium"},
     flags=["Security: a plain card ID can be cloned. Keep balances on the server and use secure cards (e.g. NTAG 424 DNA / MIFARE DESFire) for anything beyond small closed-loop amounts.",
            "Handling real money may bring legal/payment rules: describe as closed-loop tokens/credit."])

# --- Items flagged for exclusion ---------------------------------------------
idea("i074", "Door access card copied to iPhone",
     "Video claims you can add a building access card to your iPhone via Shortcuts.",
     "Shortcuts can react to a card being scanned, but cannot copy it or open a door with it.",
     [(11, "scan your card and complete the wizard... door access card will be added to your iPhone")],
     kind="tip", audience=("personal", "workplace"), goals=("access",), phone="iphone_only",
     flags=["LIKELY MISLEADING: do not publish without verifying. Apple Wallet keys only work with supported systems."])
idea("i075", "NFC rings and other wearables",
     "Tags come in ring form, so you can share info or trigger automations from your hand.",
     "A form factor, not a use case: any idea here can use a ring instead of a sticker.",
     [(8, "they even come in the form of a ring which is totally crazy")],
     kind="tip", goals=("share_info",), tag_needs=tag(form="ring"),
     flags=["Belongs in tag profiles (form factor), not ideas."])
idea("i076", "RFID-blocking wallet card",
     "A card that protects your bank cards from being read without you knowing.",
     "Shielding product, not an NFC use.",
     [(8, "stop people from going past you and skimming your credit card")],
     kind="tip", goals=("security",), tag_needs=None,
     flags=["Exclude from ideas; maybe an FAQ 'is NFC safe?' item."])
idea("i077", "Hide tags in decor",
     "Books, coasters and paintings make invisible tag holders.",
     "General placement tip.", [(9, "nfc tag right inside the cover or... coaster")], kind="tip",
     flags=["Use as a tip on results pages."])
idea("i078", "Home Assistant as the power-up",
     "With Home Assistant, a tag can control almost anything in the house.",
     "General tip.", [(14, "use home assistant you can get extremely creative... opening and closing garage doors")],
     kind="tip", setup=HA, difficulty="medium")

# ---------------------------------------------------------------- status
# hidden       = never shown (tips, unsafe or misleading entries)
# needs_review = shown, but the user still has to check a flag
# ok           = no open questions
for i in ideas:
    unsafe = any(f.startswith(("DO NOT", "LIKELY MISLEADING")) for f in i["review_flags"])
    i["status"] = "hidden" if (i["kind"] == "tip" or unsafe) else ("needs_review" if i["review_flags"] else "ok")

# ---------------------------------------------------------------- write
for name, data in [("sources", sources), ("ideas", ideas), ("idea_sources", links)]:
    with open(f"db/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

from collections import Counter
print("sources:", len(sources), "ideas:", len(ideas), "links:", len(links))
print("by kind:", Counter(i["kind"] for i in ideas))
print("flagged:", sum(1 for i in ideas if i["review_flags"]))
used = {l["source_id"] for l in links}
print("sources without ideas:", [s["id"] for s in sources if s["id"] not in used])
print("ideas without links:", [i["id"] for i in ideas if i["id"] not in {l["idea_id"] for l in links}])
