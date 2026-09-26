"""Batch 7-10: Reddit threads (added 2026-09-26 evening).

Loaded by build_db.py. Three parts:
1. REDDIT_SOURCES: one source per thread (real URLs this time)
2. NEW_IDEAS: ideas that did not exist yet
3. MAPPING: every raw NotebookLM entry -> the idea it belongs to (or None = left out, with reason)

Credit: on Reddit the idea often comes from a commenter, not the thread's author.
The link keeps the commenter's name ("credit") so the right person gets credit.
"""

RAW_FILES = {
    "D": "db/raw/batch7_reddit_sources_1-5.json",
    "F": "db/raw/batch8_reddit_sources_6-10.json",
    "R": "db/raw/batch9_reddit_sources_11-16.json",
    "C": "db/raw/batch10_reddit_sources_14_17_18.json",
    "G": "db/raw/batch11_reddit_sources_19-22.json",
}
INVENTORY = "db/raw/10_reddit_sources_inventory.json"

# ---------------------------------------------------------------- new ideas
# (id, title, summary, how, kind, audience, settings, goals, phone, setup, difficulty, cost, tag_needs overrides, business, flags)
NEW_IDEAS = [
    ("i081", "Picture cards that play music or stories", "Kids tap a picture card and their song or story starts. Screen-free, and small children can choose by themselves.",
     "Each card has a tag. A reader (or a phone/smart speaker automation) plays the song or story linked to that card.",
     "diy", ["personal"], ["home"], ["automation", "accessibility"], "any", "Home Assistant with a smart speaker, or a Raspberry Pi with a reader.", "medium", "5_to_50_eur", {"form": "card"}, None, []),
    ("i082", "A nightly lock-up round you can't half-do", "Tap a tag at each door and window during your evening check. Your phone ticks them off, so you know the round is really done.",
     "Each door/window tag marks its item as done in a checklist app, or logs the time.", "diy", ["personal"], ["home"], ["security", "tracking"], "any",
     "iPhone: Shortcuts app. Android: MacroDroid or Tasker.", "easy", "under_5_eur", {}, None, []),
    ("i084", "Know everything is closed before you leave", "One tap by the door checks every window and door sensor and tells you if something is still open.",
     "The tag triggers your smart home to read all door/window sensors and announce or notify anything left open.", "diy", ["personal"], ["home"], ["security", "automation"], "any",
     "Home Assistant (companion app on iPhone or Android).", "medium", "under_5_eur", {}, None, ["Needs door/window sensors."]),
    ("i085", "Sell NFC as a service to local businesses", "Instead of selling a card once, set up the card plus its landing page (reviews, menu, links) and keep it updated for a monthly fee.",
     "You write the tag to point at a page you control and manage that page for the business.", "business", ["nfc_as_business", "business_customers"], ["shop", "restaurant", "events"], ["marketing"], "any",
     "NFC Tools to write tags; any link-page tool for the landing pages.", "easy", "5_to_50_eur", {"form": "card"},
     {"model": "subscription_or_lease", "who": "cafes, restaurants, salons, local shops", "cost": "low"}, ["Directly related to the user's NFC review-cards leasing idea."]),
    ("i087", "Log blood pressure, oxygen or temperature in one tap", "Tap the device after measuring and your phone opens the right log with today's date ready.",
     "Tag on the blood pressure monitor, oximeter or thermometer opens a shortcut that logs the value in your health app.", "diy", ["personal"], ["home", "health"], ["tracking"], "any",
     "iPhone: Shortcuts app (Apple Health). Android: MacroDroid + your health app.", "easy", "under_5_eur", {}, None, []),
    ("i088", "Connect headphones or a speaker in one tap", "Tap the headphone case or the speaker and your phone connects to it and starts your audio.",
     "Tag triggers an automation that connects that Bluetooth device (or sets it as the audio output) and can open your music or audiobook app.", "diy", ["personal"], ["home", "office"], ["automation"], "any",
     "Android: NFC Tools Pro, MacroDroid or Bixby Routines. iPhone: Shortcuts (sets the audio output for AirPlay/AirPods).", "easy", "under_5_eur", {}, None,
     ["iPhone automations can't connect every Bluetooth device; best for AirPods/AirPlay."]),
    ("i089", "Clock in and out of work with a tap", "Tap the tag on your desk when you arrive and leave. Your hours are logged without thinking about it.",
     "The tag toggles an 'in/out' state and writes the time to a sheet, calendar or time-tracking app.", "diy", ["personal", "workplace"], ["office"], ["tracking"], "any",
     "iPhone: Shortcuts app. Android: MacroDroid or Tasker.", "easy", "under_5_eur", {}, None, []),
    ("i090", "Family chores you tick off with a tap", "Tags where the chores happen (dishwasher, bins, plants). Tap when done and everyone sees it's done. It can even become a points game.",
     "Each tag marks its chore as completed in a shared reminders list and your phone buzzes to confirm.", "diy", ["personal"], ["home"], ["tracking", "reminder"], "any",
     "iPhone: Shortcuts app + shared Reminders. Android: MacroDroid + a shared list app.", "easy", "under_5_eur", {}, None, []),
    ("i091", "Keep your habit streak with a tap", "Put a tag where the habit happens (skincare shelf, bookshelf, front door). One tap marks today as done in your habit app.",
     "Tag runs an automation that logs the habit in a habit-tracking app or counter.", "diy", ["personal"], ["home", "health"], ["tracking", "accessibility"], "any",
     "iPhone: Shortcuts app (e.g. Streaks). Android: MacroDroid + a habit app.", "easy", "under_5_eur", {}, None, []),
    ("i092", "Did anyone feed the pet?", "A tag on the food container: whoever feeds the pet taps it. Everyone can check, and the pet never gets two dinners.",
     "Tapping logs the feeding time to a shared note, sheet or calendar the whole family can see.", "diy", ["personal"], ["home", "pets"], ["tracking"], "any",
     "iPhone: Shortcuts app. Android: MacroDroid. Shared note or calendar.", "easy", "under_5_eur", {}, None, []),
    ("i093", "A care log for someone you look after", "Tags around the home for medicine, meals and toilet breaks. Each tap adds a time-stamped line to a log the whole care team can see.",
     "Each tag writes its action and the time to a shared Google Sheet.", "diy", ["personal"], ["home", "health"], ["tracking"], "any",
     "Android: MacroDroid or Tasker. iPhone: Shortcuts app. Google Sheets or similar.", "medium", "under_5_eur", {}, None, []),
    ("i094", "Remember where you parked", "Tap the tag in your car when you park and your phone saves the spot. Later it guides you back.",
     "The tag saves your current location (and can open the map to it later).", "diy", ["personal"], ["car"], ["tracking"], "any",
     "iPhone: Shortcuts app. Android: MacroDroid or Tasker.", "easy", "under_5_eur", {}, None, []),
    ("i095", "An emergency button you can always reach", "A tag by the bed or in your wallet that calls or texts a chosen person, or lights up the house, with one tap.",
     "Tag runs an automation that calls/texts an emergency contact with your location, or turns on all lights and a loud sound.", "diy", ["personal"], ["home", "health"], ["security"], "any",
     "iPhone: Shortcuts app. Android: MacroDroid. Lights part needs smart lights.", "easy", "under_5_eur", {}, None,
     ["Not a replacement for emergency services or a certified alarm."]),
    ("i096", "A treasure hunt with tags", "Hide tags around the house, garden or town. Each tap reveals the next clue. Great for kids' parties and birthdays.",
     "Each tag opens a link or map location with the next clue.", "diy", ["personal"], ["home", "outdoors", "events"], ["share_info"], "any",
     "NFC Tools (any phone).", "easy", "under_5_eur", {}, None, []),
    ("i097", "A map that opens your trip photos", "Hide tags behind places on a wall map. Tap a country and the photos from that trip open.",
     "Each tag holds the link to a shared photo album for that place.", "diy", ["personal"], ["home", "travel"], ["share_info"], "any",
     "NFC Tools (any phone).", "easy", "under_5_eur", {}, None, []),
    ("i098", "Send the robot vacuum to one spot", "Tap the tag in the kitchen, or by the litter box, and the robot vacuum cleans just that room.",
     "Tag triggers your smart home to start a room-specific clean.", "diy", ["personal"], ["home", "pets"], ["automation"], "any",
     "Home Assistant or the vacuum's app via Shortcuts/MacroDroid.", "medium", "under_5_eur", {}, None, []),
    ("i099", "The schedule you always look up, one tap away", "Bin collection days, your team's matches, today's weather: put the tag where you usually wonder about it.",
     "Tag opens the web page or app with that schedule.", "diy", ["personal"], ["home"], ["share_info"], "any",
     "NFC Tools (any phone).", "easy", "under_5_eur", {}, None, []),
    ("i100", "Know what's on each 3D printer spool", "Tag each filament spool: tap to see the material, print settings and how much is left.",
     "Each tag links to the spool's entry in a filament tracker.", "maker", ["personal"], ["home"], ["tracking"], "any",
     "Filament-tracking app or sheet; NFC Tools to write the tags.", "medium", "under_5_eur", {}, None, []),
    ("i101", "Tap a game card to see its rules", "Tags in card sleeves open the rules or a translation of foreign cards, or your whole deck list.",
     "Each tag links to the card's page or your deck list.", "diy", ["personal"], ["home", "events"], ["share_info"], "any",
     "NFC Tools (any phone).", "easy", "under_5_eur", {}, None, []),
    ("i103", "Video-call mode in one tap", "Tap before a call: desk lights set, camera and mic ready, and a 'do not disturb' light outside the door turns red.",
     "Tag runs a scene: lights for the camera, sound settings, and a status light outside.", "diy", ["personal", "workplace"], ["office", "home"], ["automation"], "any",
     "iPhone: Shortcuts app. Android: MacroDroid. Status light needs a smart bulb.", "medium", "under_5_eur", {}, None, []),
    ("i104", "Hidden sound effects and pranks", "Tap a hidden tag and a sound effect plays, or the lights do something surprising. Pure fun for guests and kids.",
     "Tag runs an automation that plays a sound or triggers a light effect.", "diy", ["personal"], ["home"], ["automation"], "any",
     "iPhone: Shortcuts app. Android: MacroDroid.", "easy", "under_5_eur", {}, None, []),
    ("i105", "The story behind something you made", "Tag a knitted piece, a craft or a gift: friends tap to see the materials, pattern and inspiration.",
     "Tag links to a page or note with the project details.", "diy", ["personal", "nfc_as_business"], ["home", "events"], ["share_info"], "any",
     "NFC Tools (any phone).", "easy", "under_5_eur", {}, None, []),
    ("i106", "Find out which clothes you really wear", "Tag your clothes and tap when you wear something. After a few months you know what to keep.",
     "Each tag logs the item as worn in a wardrobe app or sheet.", "diy", ["personal"], ["home"], ["tracking"], "any",
     "iPhone: Shortcuts app + a wardrobe app. Android: MacroDroid + a sheet.", "medium", "under_5_eur", {"form": "sticker"}, None, []),
    ("i107", "Only your card starts the car charger", "A tag by your home EV charger: charging starts only after a tap, so neighbours can't use it.",
     "The smart home enables the charger when the tag is scanned.", "diy", ["personal"], ["car", "home"], ["security", "access"], "any",
     "Home Assistant + a smart charger.", "advanced", "under_5_eur", {"waterproof": True}, None, []),
    ("i108", "Pre-heat the coffee machine from bed", "Tap the tag on your headboard and the espresso machine is warm by the time you reach the kitchen.",
     "Tag switches on a smart plug for the coffee machine.", "diy", ["personal"], ["home"], ["automation"], "any",
     "Smart plug + Shortcuts, MacroDroid or Home Assistant.", "medium", "under_5_eur", {}, None, []),
    ("i109", "Tap to pay at your craft stall", "A tag on your handmade items or stall sign opens your payment link. No card terminal needed.",
     "Tag holds your payment link (e.g. MobilePay, PayPal).", "business", ["business_customers", "nfc_as_business"], ["events", "shop"], ["payments"], "any",
     "NFC Tools (any phone).", "easy", "under_5_eur", {}, {"model": "one_time_sale", "who": "craft sellers, market stalls", "cost": "low"}, []),
]

NEW_IDEAS += [
    ("i110", "Check on your pet as you leave", "A tag by the door opens the pet camera the moment you step out, so you can see how your anxious dog is doing.",
     "Tag opens your camera app's live view (or a smart home camera dashboard).", "diy", ["personal"], ["home", "pets"], ["automation"], "any",
     "iPhone: Shortcuts app. Android: MacroDroid. Any camera app.", "easy", "under_5_eur", {}, None, []),
    ("i111", "Pay with a ring, keychain or wearable", "Tap-to-pay doesn't need a card: payment rings, keychains and watches work at any card terminal.",
     "Buy a payment wearable supported by your bank; it contains its own secure payment chip.", "product_feature", ["personal"], ["travel", "shop"], ["payments"], "any",
     None, "easy", "5_to_50_eur", {}, None, ["Never cut up or re-case bank or transit cards: use a bank-supported wearable."]),
]

# ---------------------------------------------------------------- existing ideas that grew
UPDATES = {
    "i001": {"setup_by_platform": "iPhone: Shortcuts app (set playback destination). Android: MacroDroid. Or Home Assistant.", "difficulty": "easy"},
    "i004": {"title": "Remember when you last changed or cleaned something",
             "summary": "Toothbrush heads, water filters, contact lenses, the robot vacuum's tank: tap the tag when you replace or clean it, and your phone reminds you next time.",
             "how_it_works": "Tapping saves today's date and schedules the next reminder (e.g. 90 days later).",
             "setup_by_platform": "iPhone: Shortcuts app. Android: MacroDroid. Or Home Assistant.", "difficulty": "easy"},
    "i005": {"title": "Guest mode: pause your automations", "summary": "Guests set off motion lights and doorbell alerts. One tap pauses them while people are over.",
             "how_it_works": "Tag toggles a 'guest mode' switch that your automations check before running."},
    "i014": {"title": "Set the mood: movie, dinner or game night",
             "summary": "A tag behind a painting, under the coffee table or on the board-game box sets the lights and music for that moment."},
    "i020": {"title": "Instructions exactly where you need them",
             "summary": "Tag the baby car seat, the washing machine or the fuse box: tap to open its manual or how-to video."},
    "i023": {"title": "A checklist by the door before you leave",
             "summary": "Keys, wallet, gym bag, camera batteries: tap by the door or in your bag and your checklist opens, so nothing is left behind."},
    "i038": {"title": "Switch phone settings with a tap",
             "summary": "Wifi, Bluetooth, VPN, brightness: one tap switches the settings you change all the time.", "phone_support": "android_only"},
}

# ---------------------------------------------------------------- mapping raw entry -> idea
# key: <file letter><index in that raw file>. None = left out (reason in LEFT_OUT)
MAPPING = {
    # batch 7 (D): threads 1-5
    "D0": "i042", "D1": "i014", "D2": "i004", "D3": "i020", "D4": "i009", "D5": "i010", "D6": "i016", "D7": "i014",
    "D8": "i004", "D9": "i013", "D10": "i005", "D11": "i015", "D12": "i021", "D13": "i107", "D14": "i040", "D15": "i101",
    "D16": "i108", "D17": "i028", "D18": "i027", "D19": "i041", "D20": "i091", "D21": "i006", "D22": "i031", "D23": "i003",
    "D24": "i082", "D25": "i023", "D26": "i004", "D27": "i103", "D28": "i010", "D29": "i017", "D30": "i042", "D31": "i043",
    "D32": "i049", "D33": "i009", "D34": "i028", "D35": "i035", "D36": "i035", "D37": "i040", "D38": "i038", "D39": "i036",
    "D40": "i038", "D41": "i035", "D42": "i006", "D43": "i099", "D44": "i095", "D45": "i036", "D46": "i014", "D47": None,
    "D48": "i096", "D49": "i098", "D50": "i024", "D51": None, "D52": "i109", "D53": "i044", "D54": "i044",
    # batch 8 (F): threads 6-10
    "F0": "i099", "F1": "i041", "F2": "i006", "F3": "i031", "F4": "i100", "F5": "i101", "F6": None, "F7": "i020",
    "F8": "i035", "F9": "i035", "F10": "i028", "F11": "i013", "F12": "i087", "F13": "i087", "F14": "i003", "F15": None,
    "F16": "i029", "F17": "i007", "F18": "i022", "F19": "i013", "F20": "i006", "F21": "i028", "F22": "i015", "F23": "i010",
    "F24": "i023", "F25": "i082", "F26": "i006", "F27": "i035", "F28": "i081", "F29": "i043", "F30": "i004", "F31": "i036",
    "F32": "i007", "F33": "i013", "F34": "i005", "F35": "i015", "F36": "i004", "F37": "i098", "F38": "i018", "F39": "i084",
    "F40": "i040", "F41": "i040", "F42": "i088", "F43": "i017", "F44": "i042", "F45": "i042", "F46": "i014", "F47": "i017",
    "F48": "i042", "F49": "i006", "F50": "i031", "F51": "i088", "F52": "i010", "F53": "i040", "F54": "i015", "F55": "i104",
    "F56": "i014", "F57": "i103", "F58": "i016", "F59": "i042", "F60": "i041", "F61": "i011", "F62": "i014", "F63": "i099",
    "F64": "i006", "F65": "i022", "F66": "i021", "F67": "i104", "F68": "i010", "F69": "i012", "F70": "i025", "F71": "i103",
    "F72": "i007", "F73": "i014", "F74": "i022", "F75": "i001", "F76": "i027", "F77": "i011", "F78": None, "F79": "i014",
    "F80": "i006", "F81": "i105", "F82": "i106",
    # batch 9 (R): threads 11-16
    "R0": "i041", "R1": "i016", "R2": "i081", "R3": "i015", "R4": None, "R5": "i036", "R6": "i003", "R7": "i082",
    "R8": "i084", "R9": "i028", "R10": "i006", "R11": "i004", "R12": None, "R13": "i010", "R14": "i030", "R15": None,
    "R16": "i029", "R17": "i049", "R18": "i085", "R19": "i085",
    # batch 10 (C): threads 14, 17, 18
    "C0": "i006", "C1": "i020", "C2": "i035", "C3": "i088", "C4": "i087", "C5": "i028", "C6": "i006", "C7": "i006",
    "C8": "i030", "C9": "i028", "C10": "i001", "C11": "i040", "C12": "i089", "C13": "i027", "C14": "i090", "C15": "i022",
    "C16": "i091", "C17": "i022", "C18": "i023", "C19": "i013", "C20": "i007", "C21": "i027", "C22": "i091", "C23": "i001",
    "C24": "i024", "C25": "i040", "C26": "i093", "C27": "i037", "C28": "i021", "C29": "i013", "C30": "i040", "C31": "i040",
    "C32": "i007", "C33": "i088", "C34": "i043", "C35": "i015", "C36": "i006", "C37": "i088", "C38": "i040", "C39": "i010",
    "C40": "i094", "C41": "i089", "C42": "i038", "C43": "i046", "C44": "i038", "C45": "i038", "C46": "i023", "C47": "i041",
    "C48": "i022", "C49": "i031", "C50": "i089", "C51": None, "C52": None, "C53": "i004", "C54": "i095", "C55": "i015",
    "C56": "i006", "C57": "i006", "C58": "i092", "C59": "i027", "C60": "i096", "C61": "i097", "C62": "i020", "C63": "i035",
    "C64": "i040", "C65": "i035", "C66": "i098", "C67": "i044", "C68": "i095", "C69": "i010", "C70": "i022", "C71": "i003",
    "C72": "i041", "C73": "i033", "C74": "i032", "C75": "i010", "C76": "i022", "C77": "i042", "C78": "i003", "C79": "i009",
    # batch 11 (G): threads 19-22
    "G0": "i110", "G1": "i028", "G2": "i041", "G3": "i042", "G4": "i042", "G5": "i006", "G6": "i014", "G7": "i006",
    "G8": "i025", "G9": "i043", "G10": "i090", "G11": "i042", "G12": "i004", "G13": "i022", "G14": "i081", "G15": "i015",
    "G16": "i028", "G17": "i017", "G18": "i081", "G19": "i090", "G20": "i096", "G21": "i018", "G22": "i036", "G23": "i010",
    "G24": "i004", "G25": "i021", "G26": "i028", "G27": "i023", "G28": "i020", "G29": "i022", "G30": "i095", "G31": "i017",
    "G32": "i096", "G33": "i042", "G34": "i006", "G35": "i031", "G36": "i027", "G37": "i044", "G38": "i006", "G39": "i009",
    "G40": "i100", "G41": "i004", "G42": "i044", "G43": None, "G44": "i096", "G45": None, "G46": "i020", "G47": "i035",
    "G48": "i015", "G49": "i111", "G50": None, "G51": "i111", "G52": "i105", "G53": "i111", "G54": "i111",
}

LEFT_OUT = {
    "D47": "Password generator from tags: gives a false sense of security.",
    "D51": "Password-manager trigger: security-sensitive, not for a general audience.",
    "F6": "'Encrypted' data on a normal tag: any phone can read it (same problem as i048).",
    "F15": "Selfie icebreaker: too niche.",
    "F78": "Copying game figures (Amiibo): grey area with the game maker's rules.",
    "R4": "Hand implants: medical procedure, not for a general audience.",
    "R12": "Secret audio recording: legal rules differ by country and workplace.",
    "R15": "Re-using hotel key cards as tags: a tip, not an idea (could go in tag tips).",
    "C51": "Tasker emergency kill switch: too niche.",
    "C52": "Switching Reddit accounts: too niche.",
    "G43": "Copying game figures (Amiibo): grey area with the game maker's rules.",
    "G45": "Cider dispenser that reads tagged glasses: commercial hardware, not a DIY idea.",
    "G50": "Cloning a work access card into a ring: usually against workplace security rules.",
}
