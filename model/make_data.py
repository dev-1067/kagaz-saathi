"""Builds data/train.jsonl: a compositional training set for the notice classifier.

Per class, hand-written templates with slots (banks, amounts, links, officials, dates, apps) wrapped in
ordinary SMS/WhatsApp chatter, with English, Hinglish and Devanagari variants and small typos. Written after
the frozen test set (make_fresh_test.py) and independent of it.

    python model/make_data.py
"""
import json
import random
from pathlib import Path

R = random.Random(2027)
BANKS = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "PNB", "Bank of Baroda", "Kotak", "Canara Bank", "Union Bank", "IDFC First"]
APPS = ["Paytm", "PhonePe", "Google Pay", "BHIM", "Amazon Pay", "YONO", "mobikwik"]
FAKE_LINKS = ["bit.ly/3kYc9x", "tinyurl.com/kyc-now", "sbi-kyc-verify.in", "hdfc-secure-update.co", "paytm-kyc.top", "gov-refund-india.xyz",
              "customs-clear.info", "kyc-bank-login.net", "upi-reward.club", "is.gd/Zx81Q", "bijli-pay-now.in", "indiapost-track.cc"]
OFFICIALS = ["Inspector Sharma", "Officer Verma", "Sub-Inspector Khan", "Deputy Director Rao", "Officer Singh", "Inspector Patil", "CBI officer Mehta"]
AGENCIES = ["CBI", "Mumbai Cyber Crime", "Delhi Police", "ED", "Narcotics Control Bureau", "TRAI", "Customs", "RBI", "Supreme Court", "Income Tax Department"]
COMPANIES = ["Amazon", "Flipkart", "Google", "Infosys", "TCS", "Wipro", "Reliance Jio", "Tata", "Accenture", "Swiggy", "Zomato"]
COURIERS = ["FedEx", "DHL", "India Post", "Blue Dart", "Delhivery", "Ekart", "DTDC", "Amazon"]
UTIL = ["electricity", "gas", "water", "broadband", "postpaid mobile", "DTH"]
DISCOMS = ["MSEDCL", "BSES", "Tata Power", "Adani Electricity", "TNEB", "BESCOM", "CESC"]
PHONES = ["98XXXXXX21", "70XXXXXX45", "99XXXXXX08", "88XXXXXX90", "+91 90XXXXXX12"]


def amt(lo=100, hi=90000):
    v = R.choice([R.randint(lo // 50, hi // 50) * 50, R.randint(2, 99) * 1000, R.randint(1, 20) * 10000])
    return R.choice([f"Rs {v:,}", f"Rs. {v}", f"INR {v:,}", f"₹{v:,}", f"Rs {v} only"])


def date():
    return f"{R.randint(1, 28)}-{R.choice(['Nov', 'Dec', 'Jan', 'Oct', 'Feb'])}"


def acct():
    return f"XX{R.randint(1000, 9999)}"


def s(t):
    return t.format(bank=R.choice(BANKS), app=R.choice(APPS), link=R.choice(FAKE_LINKS), off=R.choice(OFFICIALS), ag=R.choice(AGENCIES),
                    co=R.choice(COMPANIES), cour=R.choice(COURIERS), util=R.choice(UTIL), dis=R.choice(DISCOMS), ph=R.choice(PHONES),
                    a=amt(), small=amt(100, 3000), big=amt(10000, 90000), d=date(), ac=acct(), n=R.randint(100000, 999999),
                    hrs=R.choice(["1 hour", "2 hours", "24 hours", "today", "tonight", "30 minutes"]),
                    ref=R.randint(10 ** 9, 10 ** 10 - 1))


T = {
    "digital_arrest": [
        "This is {off} from {ag}. A parcel in your name contains illegal items. You are under digital arrest, stay on the video call and tell no one.",
        "{ag} notice: your Aadhaar is linked to a money laundering case. Join the video call within {hrs} or an arrest warrant will be issued.",
        "Your SIM was used for illegal activity. Do not disconnect this call. Transfer {big} to the RBI safe account to avoid arrest.",
        "Case no {ref} registered against you. {off} will interrogate you on Skype. Do not inform your family or you will be arrested.",
        "Court order: you are under house arrest. Stay online, share your screen and move your savings for verification.",
        "Aapke naam par FIR darj hai. {ag} se {off} bol raha hoon. Video call par bane rahiye aur kisi ko mat bataiye.",
        "Warrant jari ho gaya hai, giraftari se bachna hai to {big} abhi jama kijiye.",
        "{ag} अधिकारी बोल रहा हूँ। आपके खिलाफ केस दर्ज है, वीडियो कॉल पर रहें और किसी को न बताएं।",
        "Narcotics found in a courier booked with your PAN. Settle the case now by paying {big} or face arrest within {hrs}.",
        "Your number is blocked by TRAI for illegal ads. Press 9 to speak to the officer, or be arrested.",
    ],
    "kyc_block": [
        "Dear customer your {bank} account will be blocked {hrs}. Update KYC now at {link}.",
        "{bank}: PAN is not updated, account will be suspended. Click {link} and enter your card details to verify.",
        "Your {app} KYC has expired. Complete verification at {link} or the wallet will be closed.",
        "Your {bank} net banking is deactivated. Re-activate at {link} and confirm your debit card PIN.",
        "Aapka {bank} khata band ho jayega. KYC update karne ke liye {link} par click karke card number bhariye.",
        "आपका बैंक खाता बंद हो जाएगा। KYC अपडेट के लिए तुरंत लिंक पर क्लिक करें: {link}",
        "Last warning: Aadhaar not linked to your {bank} account, it will be closed {hrs}. Verify at {link}.",
        "Your {bank} reward points worth {a} expire today. Enter your PAN and net banking id at {link} to redeem.",
        "{bank} alert: account restricted due to incomplete KYC. Call {ph} and share the OTP to unlock.",
        "{app} notice: complete e-KYC by sending a photo of your Aadhaar and PAN on WhatsApp {ph}.",
    ],
    "otp_theft": [
        "Sir, I am calling from {bank}. A wrong transaction of {a} happened, read out the OTP you just received to reverse it.",
        "I sent money to you by mistake on {app}. Please approve the collect request and enter your PIN to return it, urgent.",
        "Your refund is ready. Share the 6 digit code that you will receive so that we can credit {a}.",
        "Install AnyDesk so I can fix your problem, and tell me the code that appears on your screen.",
        "Aapke phone par OTP aaya hoga, wo bata dijiye warna aapka card block ho jayega.",
        "Please tell me the verification number sent by SMS, I need it to cancel the unauthorised order.",
        "Subsidy of {small} is pending. Enter your UPI PIN on {link} to receive the money.",
        "For the cashback, scan this QR code and enter your PIN. Share the OTP with our executive.",
        "ओटीपी बताइए, मैं {bank} से बोल रहा हूँ, आपके खाते से गलत पैसे कट गए हैं।",
        "Your booking failed. Tell me the code you just received and the last four digits of your card to process again.",
    ],
    "prize_lottery": [
        "Congratulations! You won {big} in the lucky draw. Pay {small} processing fee to claim the prize.",
        "Your mobile number won an iPhone in the {co} anniversary draw. Send {small} delivery charges to receive it.",
        "You have been selected for a {big} lottery. Contact our claim officer on {ph} and pay tax first.",
        "Badhai ho! Aapne {big} ka inaam jeeta hai. Paisa nikalne ke liye {small} fees bhejiye.",
        "Dear winner, a car is yours in the festival bumper. Reply with your bank details and a fee of {small}.",
        "Free recharge worth {small} for 6 months! Fill the form at {link} and pay a small shipping fee.",
        "Lucky customer! Your number was drawn for a gift by RBI. Send your Aadhaar and {small} clearance charge.",
        "बधाई हो! आपका नंबर लॉटरी में चुना गया है। इनाम पाने के लिए अभी {small} भेजें।",
        "Scratch card winner: you won a gold coin. Pay courier cost at {link} and share your card number.",
        "{co} gift: complete the survey and win {big}. Just pay a small activation fee to receive your reward.",
    ],
    "job_fraud": [
        "Part time work from home, earn {small} daily by liking videos. Join our Telegram group and pay {small} registration.",
        "Offer letter: you are selected as executive at {co}. Deposit {small} security amount to confirm joining.",
        "Task job: rate products and earn per task. First deposit {small} to unlock the prepaid task.",
        "Congratulations on your internship at {co}. Pay {small} for ID card and laptop deposit today.",
        "Aapko {co} mein job mil gayi hai. Training fees {small} bhejiye aur joining letter lijiye.",
        "Work from home typing job, no interview, daily payment. Send {small} for software kit and start.",
        "Dear candidate your resume was shortlisted by {co}. Deposit {small} refundable fee to schedule the interview.",
        "Earn {big} per week reviewing products online. Pay {small} membership and add our manager on Telegram.",
        "घर बैठे कमाएं हज़ारों रुपये। नौकरी पक्की, बस {small} रजिस्ट्रेशन फीस जमा करें।",
        "Mega hiring, selection guaranteed. Send {small} to the HR account for medical and uniform.",
    ],
    "parcel_customs": [
        "{cour}: your parcel from abroad is held at customs. Pay {small} clearance fee at {link} to release it today.",
        "{cour}: delivery failed due to incomplete address. Update your address and pay {small} redelivery fee at {link}.",
        "Your courier contains illegal items and has been seized. Contact the customs officer and pay the penalty.",
        "{cour} notice: a package is waiting, confirm your card details to pay import duty of {small}.",
        "Aapka parcel customs mein ruka hua hai. Release ke liye {small} UPI par bhejiye.",
        "{cour}: we could not deliver your order. Reschedule by paying {small} at {link} and entering your card number.",
        "Your shipment is pending, additional duty charges {small} must be paid on the website within {hrs}.",
        "Your gift package is in the customs warehouse. Send {small} clearance fee to receive it.",
        "आपका पार्सल कस्टम में फंसा है। छुड़ाने के लिए {link} पर शुल्क दें।",
        "Gift from abroad arrived. Pay the custom clearance to our agent by UPI before it is returned.",
    ],
    "bill_cutoff": [
        "Dear consumer, your {util} connection will be disconnected tonight as last bill is unpaid. Call {ph} now.",
        "Your {util} connection will be cut off today. Update the bill by installing the support app and paying a small verification fee.",
        "{dis}: power supply to be disconnected, contact our officer immediately on {ph} and pay the pending amount at {link}.",
        "Aapka {util} ka connection aaj raat kaat diya jayega. Is number {ph} par turant sampark kijiye.",
        "{util} bill overdue: pay now on {link} or your connection will be removed with a penalty of {small}.",
        "Your mobile number will be barred in {hrs}. Pay the outstanding dues using {link} to avoid disconnection.",
        "Bill unpaid. Services will stop at midnight. Share your card details to continue the connection.",
        "बिजली का बिल जमा नहीं हुआ। आज रात कनेक्शन काट दिया जाएगा। अभी {ph} पर कॉल करें।",
        "Urgent: {dis} account suspended. Pay {small} immediately through {link} to restore supply.",
        "Final notice: electricity theft fine pending. Pay now to avoid FIR and disconnection.",
    ],
    "refund_fraud": [
        "Income Tax Department: you are eligible for a refund of {a}. Click {link} and enter your bank details.",
        "Refund pending. Verify your account number and card CVV at {link} to get the money credited.",
        "Your overpayment of {small} will be refunded. Fill the form with your net banking password.",
        "Aapka income tax refund approve ho gaya hai. Paisa pane ke liye {link} par bank details bhariye.",
        "Your bonus of {big} is ready. Pay {small} GST charges first and the amount will be credited.",
        "Excess charge refund: click {link} to claim {small} and enter your UPI PIN.",
        "Government subsidy refund waiting. Submit Aadhaar number, OTP and bank balance at the link.",
        "Your TDS refund request is stuck. Pay a processing charge of {small} and send your card details.",
        "आयकर विभाग: आपका {a} का रिफंड मंज़ूर हुआ है। पाने के लिए {link} पर बैंक डिटेल डालें।",
        "Insurance maturity money of {big} pending. Send {small} processing fee to release it today.",
    ],
    "investment_loan": [
        "Join our VIP stock group, guaranteed 300 percent returns in 15 days. Minimum investment {big} on this app.",
        "Instant loan of {big} without documents. Install the app, allow contacts access and pay {small} processing fee.",
        "Double your money in 7 days with crypto trading. Deposit {big} and our expert will trade for you.",
        "Your loan is approved. Pay insurance of {small} first, then the amount will be sent in 5 minutes.",
        "Aapko {big} ka personal loan mil sakta hai bina CIBIL ke. Pehle {small} file charges bhejiye.",
        "Invest in our IPO allotment scheme, sure profit, daily payout. Transfer to the company account and send a screenshot.",
        "Loan repayment overdue. We will message your contacts and post your photos unless you pay {small} now.",
        "Trading signal group: 90 percent accuracy, risk free. Pay {small} for VIP membership.",
        "शेयर बाज़ार में पक्का मुनाफा, पैसा दोगुना। आज ही {big} लगाइए।",
        "Pay the loan deposit now; if you delay we will call everyone in your phonebook and tell them you are a defaulter.",
    ],
    "impersonation_advance": [
        "Hello mom, this is my new number, my phone is broken. Please send {small} urgently to this account, I will explain later.",
        "Papa I am in trouble, my friend had an accident. Transfer {a} now to this number and do not tell anyone.",
        "I am calling from the {bank} fraud team. Your card was cloned, move all your savings to this safe account immediately.",
        "I am an army officer on transfer and selling my bike cheap. Send an advance of {small} on UPI and I will courier it.",
        "Your son is in police custody. Send {a} to settle it right now and do not call anyone.",
        "Bank security department here. For safety transfer your balance to the RBI protected account within {hrs}.",
        "I am stuck abroad, my wallet was stolen. Please send money to this wallet, I will return it tomorrow.",
        "Seller here, the item is yours at half price. Pay {small} token on this number first, courier follows.",
        "Beta mera naya number hai, abhi {small} bhej do urgent hai, baad mein bataunga.",
        "आपके बेटे का एक्सीडेंट हो गया है, अस्पताल में {a} तुरंत जमा करें, किसी को फोन न करें।",
        "Hi, I accidentally booked your flat for rent, pay {small} deposit to hold it, I am out of town.",
        "Sir, I am from the {bank} head office. Verify your savings by moving them to the temporary secure account today.",
    ],
    "bank_alert": [
        "Your card ending {n} has been blocked as per your request. A new card will arrive in 7 working days.",
        "Your account is temporarily locked after wrong PIN attempts. Visit a branch or use the official bank app to unlock it.",
        "{a} debited from your account at an ATM. If this was not you, call the number on the back of your card immediately.",
        "Your loan EMI of {small} failed due to low balance. Keep funds in the account before {d} to avoid charges.",
        "INR {small} debited from A/c {ac} on {d} at a merchant. Avl bal {a}. Not you? Call the number on the back of your card.",
        "Your salary of {big} has been credited to A/c {ac} on {d}. Available balance {a}.",
        "UPI payment of {small} to a shop is successful. Ref no {ref}. Bal {a}.",
        "Dear Customer, your credit card ending {n} statement of {a} is generated. Pay by {d}. Download from the official app.",
        "Your fixed deposit of {big} has matured. Proceeds credited to your savings account.",
        "{small} withdrawn from ATM on {d}. If not done by you, block your card via the bank app or helpline.",
        "आपके खाते {ac} से {small} डेबिट हुए। शेष राशि {a}।",
        "Your cheque for {a} has been cleared and credited.",
        "NEFT of {a} received in A/c {ac}. Balance {big}.",
        "EMI of {small} for your loan was debited on {d}. Next EMI is due next month.",
    ],
    "otp_notice": [
        "{n} is your OTP for login to your account. Valid for 10 minutes. Do not share it with anyone.",
        "Use code {n} to verify your {co} login. Never share this code with anyone.",
        "OTP for your transaction of {a} is {n}. Valid for 5 minutes. Do not share.",
        "Your Aadhaar OTP is {n}. It is valid for 10 minutes. UIDAI never asks for OTP over phone.",
        "आपका OTP {n} है। इसे किसी के साथ साझा न करें।",
        "{n} is your verification code. Do not forward this message.",
        "Your one time password for booking is {n}. Do not disclose it to anyone.",
        "Enter {n} to confirm your registration. If you did not request this, ignore the message.",
        "Your login OTP is {n}. Do not share it with anyone, including {bank} staff.",
        "Verification code for your {app} account: {n}. It expires in 5 minutes.",
    ],
    "bill_reminder": [
        "Your {util} bill is overdue. Pay by {d} on the official app to avoid a late fee.",
        "Society notice: water supply will be disconnected tomorrow from 10 am to 3 pm for tank cleaning.",
        "Your premium of {a} is due on {d}. The policy lapses after the grace period. Pay in the insurer's official app.",
        "Your subscription payment of {small} failed. Update your payment method in the app to avoid interruption.",
        "Your electricity bill of {a} is due on {d}. Pay through the official app or counter. Ignore if paid.",
        "Dear subscriber, your {util} bill of {small} is generated. Due date {d}. Pay on the official app.",
        "Your LPG cylinder has been booked and will be delivered within 2 days. Please keep {small} ready.",
        "Property tax of {a} is due by {d}. Pay on the municipal corporation portal. Ignore if already paid.",
        "Water bill for the month is {small}. Last date {d} without late fee.",
        "आपका बिजली बिल {a} है, अंतिम तिथि {d}। बिल का भुगतान आधिकारिक ऐप से करें।",
        "Reminder: your broadband plan renews on {d} for {small}. No action is needed if auto-pay is on.",
        "Your insurance premium of {a} is due on {d}. Pay from the insurer's official website.",
        "Society maintenance of {small} is due. Please pay at the society office or by bank transfer.",
        "DTH recharge due: your balance is low. Recharge by {d} to continue services.",
    ],
    "govt_notice": [
        "Awareness: never share your OTP or UPI PIN, and no agency arrests anyone over a video call. Report fraud on 1930.",
        "SIM re-verification is due. Visit your operator's store with your Aadhaar; it cannot be done through a link.",
        "Police verification for your passport is scheduled on {d} at your registered address. Keep documents ready.",
        "A notice has been issued for your return. View it after logging in to the official e-filing portal. Do not share your password.",
        "Your PM-KISAN instalment has been credited to your bank account. Check status at pmkisan.gov.in.",
        "Dear pensioner, please submit your Jeevan Pramaan life certificate by {d} through the bank or post office.",
        "Income Tax Department: your ITR has been processed. Check the status on the e-filing portal. Do not share your password.",
        "Aadhaar update: you can update address documents online at myaadhaar.uidai.gov.in.",
        "Voter ID: your application for correction is received. Track using the reference number on the NVSP portal.",
        "Your passport application has an appointment at the Passport Seva Kendra on {d}. Carry original documents.",
        "आपकी राशन कार्ड की ई-केवाईसी बाकी है। कृपया नजदीकी राशन दुकान पर जाकर पूरी करवाएं।",
        "GST portal: your return has been filed successfully. ARN is available in the dashboard.",
        "Municipal Corporation: water supply will be off in your ward on {d} for maintenance.",
        "Scholarship portal: your application is under verification by the institute. Update documents if marked defective.",
    ],
    "delivery_update": [
        "Your parcel was cleared. Duty of {small} was paid online on the courier's app. No further action is needed.",
        "Your order was cancelled as the item is out of stock. Refund of {a} will reflect in your original payment method in 3 days.",
        "We received your complaint about the delayed delivery. A refund of {small} will be processed in 5 to 7 working days.",
        "Your {cour} order #{ref} has been shipped and will arrive by Thursday. Track it in the app.",
        "Your package is out for delivery today. The delivery partner will call you. Keep the OTP ready only for the delivery person.",
        "{cour}: your shipment has been delivered. Thank you for shopping.",
        "Your food order is on the way, arriving in 20 minutes. Share the delivery PIN only with the rider at your door.",
        "India Post: speed post article EE{ref}IN is out for delivery.",
        "आपका ऑर्डर आज शाम तक डिलीवर होगा। ट्रैक करने के लिए ऐप खोलें।",
        "Your return pickup is scheduled for tomorrow between 10 am and 2 pm.",
        "Attempted delivery failed as you were unavailable. We will try again tomorrow.",
        "Your grocery order has been delivered. Rate your experience in the app.",
        "One item is out of stock and was removed from your order. Refund of {small} will reflect in 3 days.",
    ],
    "general": [
        "Hi, are we meeting tomorrow at 1 pm?",
        "Please find the notes attached. Tell me if anything is missing.",
        "Happy birthday! Have a great year ahead.",
        "Your class timetable has been updated on the college portal.",
        "Mummy, I reached home safely. Will call you in the evening.",
        "Appointment confirmed for Saturday 10 am at the clinic.",
        "Kal milte hain, shaam ko chai peete hain.",
        "The movie is at 7:30 pm. I booked the seats, come straight to the theatre.",
        "Exam hall ticket is available now on the university website.",
        "आज शाम घर आइए, काफी दिन हो गए।",
        "Can you send me the photos from the trip?",
        "Meeting moved to 4 pm, same room.",
    ],
}
OPEN = ["", "", "", "", "Alert: ", "Dear user, ", "Hello, ", "Important: ", "Notice: ", "Hi, ", "URGENT! ", "Sir, ", "Madam, ", "Message: "]
CLOSE = ["", "", "", "", " Regards.", " Thank you.", " Team Support.", " Do not ignore.", " Act now.", " Ignore if done."]


def typo(t):
    if R.random() < 0.1 and len(t) > 15:
        i = R.randrange(2, len(t) - 3)
        t = t[:i] + t[i + 1] + t[i] + t[i + 2:]
    if R.random() < 0.06:
        t = t.lower()
    if R.random() < 0.04:
        t = t.upper()
    return t


def main():
    rows, seen = [], set()
    for label, tpls in T.items():
        for i in range(560):
            text = typo((R.choice(OPEN) + s(tpls[i % len(tpls)]) + R.choice(CLOSE)).strip())
            if text.lower() not in seen:
                seen.add(text.lower())
                rows.append({"text": text, "label": label})
    R.shuffle(rows)
    out = Path(__file__).resolve().parent / "data" / "train.jsonl"
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print("wrote", out, len(rows))


if __name__ == "__main__":
    main()
