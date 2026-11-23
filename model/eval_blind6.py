"""Sixth message set: written after the rule changes and never tuned on, result in results/blind6_report.json.
Written by the same author as the rules, so it is fresh but not independent. Do not tune on it."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kagaz.analyzer import analyze  # noqa: E402
SCAM = [
 "Your Paytm wallet will expire. Call 9812345670 and our executive will help you complete KYC. Do not share OTP with others.",
 "This is the electricity board official portal team. Pay Rs 10 test amount on this link so that meter is not cut: bijli-pay.online",
 "Sir I sent 5,000 to your GPay by mistake, please return it. It was for my mother's hospital.",
 "You are selected for Dubai hotel job, visa and ticket free. Only medical fee 6,500 to be paid today.",
 "Customs has held your gift from London. Clearance 25,000 needed, receiver name is yours.",
 "Your SIM will be upgraded to 5G. Reply with the SIM number printed on the card and the code you get.",
 "Hi, this is HR from Infosys. Pay refundable laptop security 3,999 to confirm your joining.",
 "CBI notice: child pornography traffic traced to your IP. Reply within 24 hours with explanation or arrest warrant will be issued.",
 "Earn 3 percent daily with our AI trading bot, 500 members withdrew profit today. Minimum deposit 2,000.",
 "PM Kisan 17th instalment pending. Download pmkisan.apk and fill your bank details.",
 "Your Netflix payment failed. Update card at netflix-billing.club to avoid suspension.",
 "Didi, main Rohan ka dost hun, uska accident ho gaya hai. Hospital mein 20,000 turant jama karne hain, is number pe bhejo.",
 "बधाई हो! आपने 25 लाख की लॉटरी जीती है। राशि पाने के लिए 8,500 रुपये टैक्स भेजें।",
 "आपल्या नावाने पार्सलमध्ये ड्रग्ज सापडले आहेत. अटक टाळण्यासाठी 50,000 रुपये पाठवा.",
 "Free Covid relief of 5,000 for every ration card. Fill Aadhaar and bank details on bit.ly/relief5k and share with 10 friends.",
 "Your credit card limit is increased. Tell our agent the CVV and expiry to activate.",
 "Scan this QR code to receive your cashback of Rs 2,000, then enter UPI PIN.",
 "Madam I am from the bank's fraud cell. Someone is withdrawing money, move your balance to the secure account I give you and don't discuss with branch staff.",
 "Flat for rent 2BHK only 9,000. Owner is abroad, send token amount 5,000 to block it, keys by courier.",
 "Loan approved 5 lakh. Our official app is here, allow contacts and gallery access to disburse: quickrupee.vip"]
GENUINE = [
 "Your Jio recharge of Rs 299 is successful. Validity 28 days. Check MyJio app for details.",
 "ICICI Bank: we never ask for your OTP, PIN or CVV. Report suspicious calls to 1930.",
 "Your train 12951 is running 40 minutes late. Expected arrival 08:35.",
 "Fee reminder: second term fee of Rs 18,000 is due on 15 Dec. Pay at the school office or parent portal.",
 "Your UPI payment of Rs 340 to Sharma Kirana was successful. Ref 432198765012.",
 "Blood test report is ready. Collect it from the lab between 9 am and 6 pm.",
 "PF contribution of Rs 3,600 for October has been credited to your account.",
 "Happy birthday Aunty! Have a wonderful day.",
 "Your driving licence has been dispatched by Speed Post. Delivery in 5 days.",
 "Your electricity bill of Rs 1,870 was paid. Thank you. MSEDCL.",
 "Meeting moved to 4 pm, room 302. Please bring the printed report.",
 "Delivery attempt failed as nobody was home. We will try again tomorrow. Courier.",
 "As per RBI rules please update KYC at your branch before 31 Dec. Carry Aadhaar and PAN. No link is needed.",
 "You can exercise your right to vote on 20 Nov. Check your booth on the voter helpline app.",
 "Your scholarship application is verified by the institute and forwarded to the district office.",
 "भैया कल शाम को घर आ रहे हो क्या? माँ पूछ रही थी।",
 "आपके खाते में 12,000 रुपये वेतन जमा हुआ है।",
 "उद्या सकाळी १० वाजता सोसायटीची बैठक आहे. सर्वांनी उपस्थित राहावे.",
 "Pay your first EMI of Rs 4,250 by 5 Dec through auto debit. Keep enough balance.",
 "Congratulations on completing 5 years with us! Your service award will be given at the townhall."]
def main():
    out = {"scam_as_scam": 0, "scam_as_suspicious": 0, "scam_as_genuine": 0, "genuine_as_genuine": 0, "genuine_as_suspicious": 0, "genuine_as_scam": 0, "n": len(SCAM) + len(GENUINE), "misses": []}
    for kind, msgs in (("scam", SCAM), ("genuine", GENUINE)):
        for t in msgs:
            r = analyze(t); out[f"{kind}_as_{r['verdict']}"] += 1
            if r["verdict"] != kind:
                out["misses"].append([kind, r["verdict"], t])
    return out
if __name__ == "__main__":
    r = main(); print(json.dumps(r, ensure_ascii=False, indent=1))
    p = ROOT / "results" / "blind6_report.json"
    if not p.exists():
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
