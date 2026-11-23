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

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "data" / "stress.jsonl"
    rows = [{"text": t, "label": "genuine"} for t in GENUINE] + [{"text": t, "label": "scam"} for t in SCAM]
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print("wrote", out, len(rows))
    rows2 = [{"text": t, "label": "genuine"} for t in GENUINE2] + [{"text": t, "label": "scam"} for t in SCAM2]
    (out.parent / "stress2.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + chr(10) for r in rows2), encoding="utf-8")
