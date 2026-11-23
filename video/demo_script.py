"""Narration and visuals for Kagaz Saathi's demo video (under 3 minutes).

Each scene: (name, narration, visuals). `{cue}` switches to the visual with that cue. Numbers in {braces} come from results/*.json.
Visual kinds: ("card", name) title card · ("shot", file, start_rect, end_rect, label) 4K screenshot with a slow camera move; rect = (x, y, width)
"""
VOICE = "en-IN-NeerjaNeural"
RATE = "+2%"
FULL = (0, 0, 3840)

SCENES = [
    ("s01_problem",
     "Every day, Indians get messages like these. Your account will be blocked today. You are under digital arrest. You have won a prize. "
     "In twenty twenty five, Indians lost more than twenty thousand crore rupees to cyber fraud, and the person who gets the message "
     "usually has nobody to ask. {intro} This is Kagaz Saathi. Ask Kagzi first.",
     [(None, ("card", "problem")), ("intro", ("card", "intro"))]),

    ("s02_landing",
     "Paste any message, or snap a photo of a letter or bill. Kagzi tells you if it is real, explains it in your own language, "
     "and tells you what to do next.",
     [(None, ("shot", "v01_landing.png", FULL, (200, 120, 3300), "Kagaz Saathi · landing page"))]),

    ("s03_scam",
     "Here is a fake bank message. Kagzi marks it a scam, gives a risk score, and lists exactly why. It asks for card details, "
     "it threatens to block the account, and the link only looks like a bank site.",
     [(None, ("shot", "v05_check_scam.png", FULL, (1900, 330, 1900), "A fake KYC message: very likely a scam"))]),

    ("s04_hindi",
     "The same answer in Hindi, or Marathi, read aloud, with clear steps and one tap to the national cyber fraud helpline, nineteen thirty.",
     [(None, ("shot", "v06_check_hindi.png", (1700, 250, 2100), (1900, 330, 1900), "Hindi · Marathi · English, read aloud"))]),

    ("s05_genuine",
     "A real one time password message is recognised and left alone, with the good sign pointed out. So Kagzi does not cry wolf.",
     [(None, ("shot", "v07_check_genuine.png", FULL, (1900, 330, 1900), "A real OTP message: looks genuine"))]),

    ("s06_family",
     "Scammers say, do not tell anyone. Kagzi does the opposite. It writes the alert for your son or daughter, with the verdict and what to do, ready to send on WhatsApp.",
     [(None, ("shot", "v08_family.png", FULL, (1900, 330, 1900), "Family loop: nobody faces a scam alone"))]),

    ("s06b_share",
     "Most scams arrive on WhatsApp. So on a phone, tap Share on any message, choose Kagzi, and it opens already checked. No copying, no typing.",
     [(None, ("shot", "v12_share.png", FULL, (200, 120, 3300), "Share any WhatsApp message to Kagzi"))]),

    ("s07_dashboard",
     "Every check is saved to your account, with a dashboard of what was caught, {hist} a history you can search, and a guide to the ten scams people fall for most.",
     [(None, ("shot", "v04_dashboard.png", FULL, (300, 100, 3300), "Dashboard and history")),
      ("hist", ("shot", "v09_history.png", FULL, (300, 100, 3300), "History"))]),

    ("s08_accuracy",
     "Under the hood is a small trained model. It scores {acc} percent on one hundred and fifty messages it was not trained on. "
     "{stress} Then we wrote forty harder messages. It flagged every scam, and was too cautious with four real ones. The accuracy page shows exactly that.",
     [(None, ("shot", "v10_accuracy.png", FULL, (300, 150, 3300), "Model accuracy, trained and tested")),
      ("stress", ("shot", "v11_accuracy2.png", FULL, (300, 150, 3300), "Hard stress tests"))]),

    ("s09_aws",
     "And it is live on AWS. One Lambda function behind a public URL, DynamoDB for accounts and history, and one template that deploys everything, "
     "tested end to end on the real deployment.",
     [(None, ("card", "aws"))]),

    ("s10_outro",
     "Kagaz Saathi. Ask Kagzi first.",
     [(None, ("card", "outro"))]),
]
