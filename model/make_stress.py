"""Writes data/stress.jsonl: 40 deliberately tricky hand-written messages (20 genuine that sound scary, 20 scams written
in unusual wording). Frozen before any tuning against it; reported as-is in docs and the accuracy page.

    python model/make_stress.py
"""
import json
from pathlib import Path

GENUINE = [
    "Your electricity bill is overdue. Pay by 28-Nov on the official MSEDCL app to avoid a late fee.",
    "ALERT: Rs 18,000 debited from your account XX5521 at an ATM. If this was not you, call the number on the back of your card immediately.",
    "Your credit card ending 4410 has been blocked as per your request. A new card will arrive in 7 working days.",
    "Income Tax Department: a notice under section 143(1) has been issued. View it after logging in to the e-filing portal. Do not share your password.",
    "Your Aadhaar mobile number update request is received. Visit the nearest Aadhaar Seva Kendra with ID proof by 05-Dec.",
    "Dear customer, your SIM KYC re-verification is due. Visit your operator's store with your Aadhaar; it cannot be done over a link.",
    "Your IRCTC ticket PNR 8412345678 is waitlisted. If not confirmed, the refund will be credited automatically within 7 days.",
    "Final reminder: your term insurance premium of Rs 9,800 is due on 30-Nov. Policy lapses after the grace period. Pay in the insurer's official app.",
    "Your loan EMI of Rs 6,432 failed due to insufficient balance. Please keep funds in the account before 05-Dec to avoid charges.",
    "We have received your complaint about the delayed delivery. A refund of Rs 799 will be processed in 5 to 7 working days.",
    "Your account has been temporarily locked after three wrong PIN attempts. Visit a branch or use the bank's official app to unlock it.",
    "Customs: your declared parcel was cleared. Duty of Rs 1,450 was paid online on the courier's app. No further action needed.",
    "Police verification for your passport is scheduled on 03-Dec at your registered address. Keep your original documents ready.",
    "Your Netflix payment of Rs 649 failed. Update your payment method in the Netflix app to avoid interruption.",
    "OTP 482910 for your Rs 25,000 transfer to Rajesh Kumar. If you did not request this, do not share the OTP and call your bank.",
    "Cyber crime awareness: never share your OTP or UPI PIN, and no agency conducts arrests over video calls. Report fraud on 1930.",
    "Dear student, your scholarship application has been marked defective. Upload the corrected income certificate on the portal by 10-Dec.",
    "Your EPF claim of Rs 1,20,000 has been settled and credited to your bank account on 14-Nov.",
    "Society notice: water supply will be disconnected tomorrow from 10 am to 3 pm for tank cleaning.",
    "Your Amazon order was cancelled as the item is out of stock. Refund of Rs 2,199 will reflect in your original payment method in 3 days.",
]
SCAM = [
    "Sir, there is a pending case against your Aadhaar. To close it quietly, send a small amount as guarantee to this account today.",
    "Your child was found with drugs at the airport. Do not call the school or anyone. Transfer money now for the lawyer.",
    "You have been chosen for our paid review programme. Pay a refundable activation of 999 on this QR and earn 2,000 per hour.",
    "I am Colonel Sharma, army canteen. Selling my scooter cheap because of transfer, send an advance on UPI and I will courier it.",
    "Hello mom, this is my new number, my phone broke. Please urgently send 15,000 to this account, I will explain later.",
    "Your electricity meter will be replaced. Our engineer needs a small fee on this number before visiting. Shut the meter if you refuse.",
    "Verify your SIM by forwarding the code you get on WhatsApp to this number, otherwise it will be deactivated today.",
    "Free electricity scheme from the government. Register on this link with your card number and the one time password we send.",
    "Dear sir, your son got an accident, pay hospital deposit immediately on this number, do not call anyone, it is urgent.",
    "Congrats! Your resume is selected for a government job, no exam. Pay the form fee of Rs 1,500 on this UPI id to confirm.",
    "Your phone number won the bumper gift from the electronics store. Send the GST and delivery of Rs 2,900 to receive it.",
    "Your credit limit has been increased to 5 lakh. Share the card's last digits and the code sent to you to activate it.",
    "Click here to track your pension. Your pension is stopped and will be restarted after you enter your bank login at this site.",
    "Help me, I am stuck abroad and my wallet was stolen. Please send money on this crypto wallet, I will return it tomorrow.",
    "Your Gas subsidy of 2,500 is blocked. Pay 100 to release it using the link below and enter your UPI PIN.",
    "Special offer for you: invest 50,000 today and get 1 lakh in ten days, our CA guarantees it. WhatsApp only.",
    "Hello, I am from the bank's fraud team. Your card was cloned, so please move all savings to this safe account now.",
    "You have unclaimed insurance money. To receive it, keep this call confidential and pay the legal clearance.",
    "A voter ID update is mandatory. Install this APK file to complete it before midnight or your name will be deleted.",
    "Order confirmation: you purchased an iPhone for 74,999. If this was not you, click here to cancel and enter your card details.",
]

# Second stress set, written after the first one was used to find weaknesses, so it measures the fixes fairly.
GENUINE2 = [
    "Your Jio recharge of Rs 299 expired yesterday. Recharge in the MyJio app to keep your services active.",
    "Your debit card will expire on 12/26. A replacement has been dispatched to your registered address.",
    "Alert: login to your account from a new device. If this was not you, change your password in the official app right away.",
    "The court hearing for case no. 2210 is on 14-Dec at 10:30 am. Please carry the original summons.",
    "Your mutual fund SIP of Rs 5,000 failed this month because of low balance. It will be retried on 03-Dec.",
    "Your gas cylinder delivery is delayed by one day because of a strike. We apologise for the inconvenience.",
    "Dear parent, school fees of Rs 14,500 are due on 30-Nov. Please pay on the school portal. A late fee applies after that date.",
    "Your PAN card application was received. It will be dispatched in 15 days. Track on the NSDL website.",
    "Your phone insurance claim has been approved and a repair appointment is booked for Saturday.",
    "A traffic challan of Rs 500 has been issued to your vehicle. Pay on the official Parivahan website within 60 days.",
]
SCAM2 = [
    "I am the new manager at your gym. Your membership refund is held, send 500 as an identity check on this number to release it.",
    "Auntie, it is Rahul your neighbour's son, I am in hospital with a broken leg, please send 8,000 on this number right now.",
    "Your WhatsApp will expire tonight. Forward this message to ten groups and tap the link to renew for life.",
    "Dear Sir, your PAN will be cancelled and a fine will be levied. Upload your selfie holding the card at this link.",
    "Rent your spare room to foreign students. They will send an extra cheque; just return the balance by transfer.",
    "Your Amazon Prime order for a laptop worth 1,10,000 was placed. To dispute, call our helpdesk on this number and install the support app.",
    "Hello, I found your lost wallet. For the courier of the wallet, send 300 to this account and I will ship it.",
    "Last date to claim your tax rebate is today. Submit your net banking user id to the officer on the link.",
    "You are shortlisted for a loan waiver by the government. Pay the verification amount of Rs 750 first.",
    "Complaint registered against your number in the cyber cell. Press 1 now to speak with the officer or your SIM will be blocked.",
]


# Third stress set: 30 new messages, written and frozen BEFORE the second round of fixes (hard negatives, new scam styles, rules).
GENUINE3 = [
    "Your Airtel number will be barred on 05-Dec as your KYC is incomplete. Visit an Airtel store with your Aadhaar. KYC cannot be completed over a link or call.",
    "IRCTC: your ticket PNR 6123456789 has been cancelled as per your request. Refund of Rs 1,120 will be credited to your original payment source in 4-5 days.",
    "Your EPF passbook shows a new contribution of Rs 3,850 for October. Log in at the official EPFO member portal to view it.",
    "Dear parent, the PTA meeting is on 29-Nov at 11 am in the school hall. Kindly attend.",
    "Your hospital appointment with Dr. Mehta is confirmed for Tuesday 10 am. Please bring your reports and insurance card.",
    "Your car insurance renews on 12-Dec. Premium Rs 14,300. Pay in the insurer's official app or at any branch; ignore if already paid.",
    "Your electricity meter reading for November is 5,412 units. Bill of Rs 2,260 will be generated on 01-Dec.",
    "Your Amazon Pay UPI transaction of Rs 249 to Jio Recharge was successful. If you did not do this, contact your bank at once.",
    "Reminder: your driving licence expires on 31-Dec. Renew it on the official Parivahan portal before that date.",
    "Your Swiggy account password was changed. If this was not you, reset it from the app or call Swiggy support from the app.",
    "SBI: Your debit card ending 3392 will expire next month. A new card has been dispatched to your registered address.",
    "Dear member, your gym membership ends on 30-Nov. Renew at the front desk to continue.",
    "GST portal: your notice DRC-01 is available under View Notices. Reply within 15 days. Never share your login credentials with anyone.",
    "Your scholarship amount of Rs 12,000 has been credited to your Aadhaar-linked bank account.",
]
SCAM3 = [
    "Hello sir, I am calling for the electricity subsidy. To get Rs 2,000 monthly, scan this QR code and enter your UPI PIN to confirm your account.",
    "E-challan of Rs 1,500 pending for your vehicle. Pay within 2 hours at echallan-parivahan.top or your licence will be suspended.",
    "Your Google Pay account is under review. Share the screen with our executive using this app to avoid permanent closure.",
    "Dear user, your Aadhaar is locked for suspicious activity. Call 90XXXXXX11 and read the code you receive to unlock it.",
    "Donate for flood victims today and win a free gift. Transfer any amount to this personal UPI id, receipt will follow on WhatsApp.",
    "We found a virus on your phone. Install the antivirus APK from this link right now or all your photos will be deleted.",
    "Bhai mera account freeze ho gaya hai, tum apna UPI PIN bhej do, main kuch der me wapas kar dunga, bahut urgent hai.",
    "Congratulations, your number is selected for a free 5G sim. Pay Rs 99 delivery on this link and enter your card number.",
    "Your parcel has an unpaid duty. Our courier agent will visit; pay Rs 1,800 to him by UPI first or the parcel is returned.",
    "Customer care alert: to cancel your wrong online order of Rs 18,000, tell us the OTP and the card CVV right now.",
    "I am an officer with the Income Tax Department. A case is filed against you; settle it today by gift cards worth Rs 40,000 or face arrest.",
    "Work from home as a parcel packer, Rs 800 per hour. Pay Rs 1,200 training kit fee to our manager on WhatsApp and start tomorrow.",
    "Your bank says KYC expired. Use our faster link to reverify: sbi-kyc-fast.in. Do it in 30 minutes, otherwise your balance will be frozen.",
    "You are eligible for a government laptop scheme. Register with Aadhaar, PAN and bank PIN at this link before midnight.",
    "Your cousin lost his wallet in Dubai and cannot call you. He asked me to ask you to send Rs 20,000 to this account; do not tell the family.",
    "Hi, this is your delivery partner. I am outside but need Rs 50 more by UPI first, then I will give your parcel.",
]

# Fourth stress set: 24 new messages, written and frozen before the second round of fixes, so it can measure them fairly.
GENUINE4 = [
    "Your Kotak account statement for October is ready. Download it from the official app. We never ask for your PIN or OTP.",
    "Dear customer, your gas cylinder refill has been delivered. If you did not receive it, call the number on your gas card.",
    "Your Aadhaar update request URN 1234-5678 has been approved. Download the updated Aadhaar from the official UIDAI website.",
    "Your PhonePe payment of Rs 560 to Metro Pharmacy was successful. UPI Ref 48291033.",
    "Your semester exam fee of Rs 1,350 is due on 05-Dec. Pay on the college portal. A late fee applies after that date.",
    "Your Zomato order has been cancelled by the restaurant. Rs 340 will be refunded to your original payment method within 3 days.",
    "We have received your rent payment of Rs 12,000 for November. Thank you, Sharma Properties.",
    "Dear sir, your pension for November has been credited to your account XX7745. Ref no 221178.",
    "Your flight 6E 204 to Pune on 02-Dec is delayed by 40 minutes. New departure 18:40. Sorry for the inconvenience.",
    "Your application for the PM Awas subsidy has been verified. You will be contacted by the bank for the next step.",
    "Your Wi-Fi router will be replaced on 30-Nov between 2 and 5 pm. A technician from the company will visit; please keep an adult at home.",
    "Hi Sir, your bike service is complete. Total Rs 2,150. Please collect it before 7 pm.",
]
SCAM4 = [
    "Dear customer your electricity bill will not be updated, so your power will be cut tonight. To update, call our officer on 96XXXXXX20 at once.",
    "Sir your Aadhaar will be deactivated within 24 hours. Click here and enter your Aadhaar number, mobile and the OTP to stop deactivation.",
    "Hello, I am from Amazon customer support. Your account was hacked. Please install QuickSupport so that I can secure your bank account.",
    "You have won Rs 8 lakh in the Reliance Jio lucky draw. To release the prize send Rs 3,000 as GST to this account today.",
    "Earn Rs 3,000 daily by watching ads. Join this Telegram channel and pay Rs 700 for the starter kit to begin.",
    "Your son has been arrested for a road accident and the police need Rs 60,000 to settle it right now. Do not call his number.",
    "Your PF withdrawal of Rs 1.5 lakh is approved. Pay the Rs 4,500 processing fee to our agent first and the money comes in minutes.",
    "Final notice from the Supreme Court: your SIM was used in a fraud. Join the video call with the judge today or a warrant is issued.",
    "Get a personal loan of Rs 2 lakh in 10 minutes without any documents. Pay Rs 2,000 insurance and download this loan APK.",
    "This is the bank's security desk. Your card was used abroad. Share the code we just sent so we can stop the transaction.",
    "Free gold coin for every customer today. Pay Rs 150 courier charge by UPI on this number and share your address.",
    "Your FASTag is blocked. Recharge now through this link: fastag-recharge-help.xyz and enter your card details to unblock.",
]

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "data" / "stress.jsonl"
    rows = [{"text": t, "label": "genuine"} for t in GENUINE] + [{"text": t, "label": "scam"} for t in SCAM]
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print("wrote", out, len(rows))
    rows2 = [{"text": t, "label": "genuine"} for t in GENUINE2] + [{"text": t, "label": "scam"} for t in SCAM2]
    (out.parent / "stress2.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + chr(10) for r in rows2), encoding="utf-8")
    rows3 = [{"text": t, "label": "genuine"} for t in GENUINE3] + [{"text": t, "label": "scam"} for t in SCAM3]
    (out.parent / "stress3.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + chr(10) for r in rows3), encoding="utf-8")
    print("wrote stress2.jsonl and stress3.jsonl", len(rows3))
    rows4 = [{"text": t, "label": "genuine"} for t in GENUINE4] + [{"text": t, "label": "scam"} for t in SCAM4]
    (out.parent / "stress4.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + chr(10) for r in rows4), encoding="utf-8")
    print("wrote stress4.jsonl", len(rows4))
