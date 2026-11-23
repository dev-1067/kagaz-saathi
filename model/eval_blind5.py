"""Fifth message set, written after every rule was frozen at commit efafd7b and scored once at that commit.
Written by the same AI assistant that helped build the rules, so it is fresh but not independent."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kagaz.analyzer import analyze  # noqa: E402
SCAM = [
 "Sir your FASTag KYC is pending. Wallet will stop at toll. Complete here fastag-verify-kyc.com",
 "I am calling from TRAI, your Aadhaar was used to take 14 SIM cards. Press 9 to talk to Mumbai cyber crime officer.",
 "Dear pensioner, your pension will stop from December. Send PPO number, card number and OTP to our officer to continue.",
 "Good morning, I saw your flat on 99acres. I am an army officer posted in Jammu, I will pay rent in advance, just scan the QR I send.",
 "Papa mera phone toot gaya, ye naya number hai. Jaldi 8000 is UPI pe bhej do, baad mein batata hun.",
 "You have an unclaimed dividend of Rs 48,900. Verify bank details and pay 2 percent stamp duty to receive it.",
 "Your gas connection will be cut tonight as last month bill not updated. Contact gas officer 8877665544.",
 "Join our WhatsApp group for IPO allotment, 100 percent confirmed allotment, deposit through our app only.",
 "Hello, part time work from home. Like YouTube videos and earn 150 per like. First task free. Message on Telegram.",
 "आपका बिजली कनेक्शन आज रात 9 बजे काट दिया जाएगा, तुरंत अधिकारी से 9123456780 पर संपर्क करें",
 "तुमचे बँक खाते आज बंद होईल. KYC अपडेट करण्यासाठी या लिंकवर क्लिक करा bit.ly/kycmr",
 "Your income tax refund of 15,490 is approved. Submit account details at incometax-refund-claim.xyz",
 "Instant loan 2 lakh without CIBIL. Pay Rs 1,499 file charge to release amount.",
 "We found your number in a money laundering case. Transfer your savings to the RBI verification account, it will be returned after inquiry.",
 "Your parcel has been returned because house number is missing. Update address and pay Rs 5 at indiapost-redelivery.top",
 "Please visit the official website and stay on the line, then transfer the amount to the safe account given by our officer.",
 "Your account is under review and may be frozen. Use our official app from the link I send and log in with your details.",
 "Bank manager speaking. Your card reward points expire tonight. Tell me the 6 digit number you just got to redeem.",
 "Madam, your courier contains illegal passports. Join Skype with narcotics department or warrant will be issued.",
 "Win an iPhone! You are today's lucky visitor, pay only Rs 99 shipping."]
GENUINE = [
 "Your HDFC Bank credit card statement is ready. Total due Rs 12,430. Due date 5 Dec. Pay through the app or net banking.",
 "Reminder: your Aadhaar enrolment centre appointment is on 2 Dec at 11 am. Carry original documents.",
 "Hi beta, reached home safely. Call me when free.",
 "Your Amazon order has been shipped and will arrive on Thursday. Track it in the app.",
 "Dear parent, school will remain closed on Friday due to heavy rain. Regards, Principal.",
 "Rs 2,500 debited from A/c XX4521 on 21-Nov to Swiggy via UPI. Not you? Call the number on your card.",
 "Your LIC premium of Rs 6,200 is due on 10 Dec. Pay at any LIC branch or licindia.in.",
 "338201 is your OTP to log in to DigiLocker. Do not share it with anyone.",
 "Your car insurance expires on 30 Nov. Renew on the insurer's website or through your agent to avoid a break in cover.",
 "Water supply will be shut on Sunday from 10 am to 4 pm for pipeline repair. BMC.",
 "Your passport police verification is complete. Status can be checked at passportindia.gov.in.",
 "Can you send me the notes from today's class? I missed the lecture.",
 "आपकी गैस बुकिंग स्वीकार हो गई है। सिलेंडर 2 दिन में मिलेगा।",
 "तुमचा वीज बिल रु 1,240 आहे. अंतिम तारीख 5 डिसेंबर. महावितरण ॲपवर भरा.",
 "Your SIP of Rs 5,000 in Axis Bluechip Fund has been processed. Units will be allotted in 2 days.",
 "Your account has been locked after 3 wrong password attempts. It will unlock in 24 hours, or visit your branch.",
 "Mummy ne kaha hai aate waqt doodh aur bread le aana.",
 "Final notice: property tax for 2026-27 must be paid by 31 Dec. Pay at the ward office or the municipal website.",
 "Your job application for Analyst has been received. We will contact shortlisted candidates by email.",
 "Dr Mehta's clinic: your appointment is confirmed for 6 pm tomorrow. Reply C to cancel."]
def main():
    c = {}
    for kind, msgs in (("scam", SCAM), ("genuine", GENUINE)):
        for t in msgs:
            r = analyze(t); k = kind + "->" + r["verdict"]; c[k] = c.get(k, 0) + 1
            if (kind == "scam" and r["verdict"] != "scam") or (kind == "genuine" and r["verdict"] != "genuine"):
                print(f"  {k:20} {r['model']} {r['signals']} | {t[:95]}")
    print(c); return c
if __name__ == "__main__":
    main()
