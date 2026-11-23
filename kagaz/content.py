"""Plain-language content for every notice type, in English, Hindi and Marathi, plus helplines and official domains.

Fixed text written for this project (nothing is translated at run time) and kept short. Not yet reviewed by a native Hindi/Marathi speaker.
"""
SCAM = {"digital_arrest", "kyc_block", "otp_theft", "prize_lottery", "job_fraud", "parcel_customs", "bill_cutoff", "refund_fraud",
        "investment_loan", "impersonation_advance"}

LABELS = {
    "digital_arrest": {"en": "Fake 'digital arrest' call", "hi": "फर्ज़ी 'डिजिटल अरेस्ट' कॉल", "mr": "बनावट 'डिजिटल अरेस्ट' कॉल"},
    "kyc_block": {"en": "Fake KYC / account-block message", "hi": "फर्ज़ी KYC / खाता बंद संदेश", "mr": "बनावट KYC / खाते बंद संदेश"},
    "otp_theft": {"en": "OTP / UPI PIN theft attempt", "hi": "OTP / UPI PIN चुराने की कोशिश", "mr": "OTP / UPI PIN चोरीचा प्रयत्न"},
    "prize_lottery": {"en": "Fake prize or lottery", "hi": "फर्ज़ी इनाम या लॉटरी", "mr": "बनावट बक्षीस किंवा लॉटरी"},
    "job_fraud": {"en": "Fake job or task offer", "hi": "फर्ज़ी नौकरी या टास्क ऑफर", "mr": "बनावट नोकरी किंवा टास्क ऑफर"},
    "parcel_customs": {"en": "Fake parcel / customs notice", "hi": "फर्ज़ी पार्सल / कस्टम नोटिस", "mr": "बनावट पार्सल / कस्टम नोटीस"},
    "bill_cutoff": {"en": "Fake bill cut-off threat", "hi": "फर्ज़ी बिल कनेक्शन कटने की धमकी", "mr": "बनावट बिल कनेक्शन तोडण्याची धमकी"},
    "refund_fraud": {"en": "Fake refund or bonus", "hi": "फर्ज़ी रिफंड या बोनस", "mr": "बनावट रिफंड किंवा बोनस"},
    "investment_loan": {"en": "Investment / loan-app fraud", "hi": "निवेश / लोन ऐप धोखाधड़ी", "mr": "गुंतवणूक / लोन ॲप फसवणूक"},
    "impersonation_advance": {"en": "Impersonation / urgent-money scam", "hi": "रिश्तेदार या अधिकारी बनकर पैसे मांगने की ठगी", "mr": "नातेवाईक किंवा अधिकारी बनून पैसे मागण्याची फसवणूक"},
    "bank_alert": {"en": "Bank transaction alert", "hi": "बैंक लेन-देन सूचना", "mr": "बँक व्यवहार सूचना"},
    "otp_notice": {"en": "One-time password (OTP) message", "hi": "वन-टाइम पासवर्ड (OTP) संदेश", "mr": "वन-टाइम पासवर्ड (OTP) संदेश"},
    "bill_reminder": {"en": "Bill or payment reminder", "hi": "बिल / भुगतान अनुस्मारक", "mr": "बिल / देयक स्मरणपत्र"},
    "govt_notice": {"en": "Government / official notice", "hi": "सरकारी / आधिकारिक सूचना", "mr": "सरकारी / अधिकृत सूचना"},
    "delivery_update": {"en": "Delivery update", "hi": "डिलीवरी अपडेट", "mr": "डिलिव्हरी अपडेट"},
    "general": {"en": "Ordinary personal message", "hi": "सामान्य निजी संदेश", "mr": "सामान्य वैयक्तिक संदेश"},
}

WHY = {
    "digital_arrest": {"en": "No police, CBI, ED or court arrests anyone over a video call or asks for money to 'close a case'. This is a well-known scam called 'digital arrest'.",
                       "hi": "कोई भी पुलिस, CBI, ED या अदालत वीडियो कॉल पर गिरफ्तारी नहीं करती और न ही केस बंद करने के लिए पैसे मांगती है। यह 'डिजिटल अरेस्ट' नाम का जाना-पहचाना धोखा है।",
                       "mr": "कोणतेही पोलीस, CBI, ED किंवा न्यायालय व्हिडिओ कॉलवर अटक करत नाही आणि केस बंद करण्यासाठी पैसे मागत नाही. ही 'डिजिटल अरेस्ट' नावाची सर्वपरिचित फसवणूक आहे."},
    "kyc_block": {"en": "Banks do not block accounts through a link in an SMS. The link leads to a fake page that steals your card, PIN or OTP.",
                  "hi": "बैंक SMS में लिंक भेजकर खाता बंद नहीं करते। लिंक नकली पेज पर ले जाता है जो आपका कार्ड, PIN या OTP चुरा लेता है।",
                  "mr": "बँका SMS मधील लिंकद्वारे खाते बंद करत नाहीत. लिंक बनावट पेजवर नेते जे तुमचे कार्ड, PIN किंवा OTP चोरते."},
    "otp_theft": {"en": "Anyone asking for your OTP, UPI PIN or card details is a fraudster. A real bank or app never asks for them. To RECEIVE money you never enter a PIN.",
                  "hi": "जो भी आपसे OTP, UPI PIN या कार्ड की जानकारी मांगे वह ठग है। असली बैंक या ऐप कभी नहीं मांगते। पैसे पाने के लिए PIN कभी नहीं डालना पड़ता।",
                  "mr": "तुमचा OTP, UPI PIN किंवा कार्ड तपशील मागणारा फसवणूक करणारा असतो. खरी बँक किंवा ॲप कधीही मागत नाही. पैसे मिळवण्यासाठी PIN टाकावा लागत नाही."},
    "prize_lottery": {"en": "You cannot win a lottery you never entered, and real prizes never need a fee first. Paying 'tax' or 'delivery charge' is how the fraud works.",
                      "hi": "जिस लॉटरी में आपने भाग ही नहीं लिया उसे आप जीत नहीं सकते, और असली इनाम के लिए पहले फीस नहीं देनी पड़ती। 'टैक्स' या 'डिलीवरी चार्ज' भरवाना ही ठगी है।",
                      "mr": "ज्या लॉटरीत भाग घेतला नाही ती जिंकता येत नाही, आणि खऱ्या बक्षिसासाठी आधी फी भरावी लागत नाही. 'कर' किंवा 'डिलिव्हरी चार्ज' भरायला लावणे हीच फसवणूक आहे."},
    "job_fraud": {"en": "Real employers never charge a registration, security or training fee, and never pay for 'liking videos' or 'rating products'. Task jobs first take your deposit, then disappear.",
                  "hi": "असली कंपनियां रजिस्ट्रेशन, सिक्योरिटी या ट्रेनिंग फीस नहीं लेतीं और वीडियो लाइक करने के पैसे नहीं देतीं। टास्क जॉब पहले आपका डिपॉज़िट लेते हैं, फिर गायब हो जाते हैं।",
                  "mr": "खऱ्या कंपन्या नोंदणी, सुरक्षा किंवा प्रशिक्षण फी घेत नाहीत आणि व्हिडिओ लाईक करण्याचे पैसे देत नाहीत. टास्क नोकऱ्या आधी डिपॉझिट घेतात आणि नंतर गायब होतात."},
    "parcel_customs": {"en": "Couriers and customs do not collect fees through random links or UPI numbers, and customs never threatens arrest by message. Check the tracking number on the courier's official app.",
                       "hi": "कूरियर कंपनी या कस्टम विभाग अनजान लिंक या निजी UPI नंबर पर फीस नहीं मंगवाते और मैसेज से गिरफ्तारी की धमकी नहीं देते। ट्रैकिंग नंबर कूरियर के आधिकारिक ऐप पर जांचें।",
                       "mr": "कुरिअर कंपनी किंवा कस्टम विभाग अनोळखी लिंक किंवा खासगी UPI नंबरवर फी मागत नाहीत आणि मेसेजने अटकेची धमकी देत नाहीत. ट्रॅकिंग नंबर कुरिअरच्या अधिकृत ॲपवर तपासा."},
    "bill_cutoff": {"en": "Electricity, gas and water boards do not disconnect connections 'tonight' on the basis of a message asking you to call a personal number or install an app.",
                    "hi": "बिजली, गैस और पानी विभाग किसी निजी नंबर पर कॉल करने या ऐप डाउनलोड करने को कहकर 'आज रात' कनेक्शन नहीं काटते।",
                    "mr": "वीज, गॅस आणि पाणी विभाग वैयक्तिक नंबरवर कॉल करायला किंवा ॲप इन्स्टॉल करायला सांगून 'आज रात्री' कनेक्शन तोडत नाहीत."},
    "refund_fraud": {"en": "Tax and government refunds are credited straight to your registered bank account. They never ask you to click a link, pay a 'processing charge' or share your card details.",
                     "hi": "टैक्स या सरकारी रिफंड सीधे आपके पंजीकृत बैंक खाते में आता है। इसके लिए लिंक क्लिक करने, 'प्रोसेसिंग चार्ज' देने या कार्ड की जानकारी देने को नहीं कहा जाता।",
                     "mr": "कर किंवा सरकारी रिफंड थेट तुमच्या नोंदणीकृत बँक खात्यात जमा होतो. त्यासाठी लिंक क्लिक करणे, 'प्रोसेसिंग चार्ज' भरणे किंवा कार्ड तपशील देणे सांगितले जात नाही."},
    "investment_loan": {"en": "'Guaranteed' or 'double your money' returns do not exist. Loan apps that ask for contact access or an advance fee are used for blackmail and theft.",
                        "hi": "'पक्का मुनाफा' या 'पैसा दोगुना' जैसी चीज़ें नहीं होतीं। संपर्क-सूची की अनुमति या अग्रिम फीस मांगने वाले लोन ऐप ब्लैकमेल और चोरी के लिए इस्तेमाल होते हैं।",
                        "mr": "'हमखास नफा' किंवा 'पैसे दुप्पट' असे काही नसते. संपर्क यादीची परवानगी किंवा आगाऊ फी मागणारे लोन ॲप ब्लॅकमेल आणि चोरीसाठी वापरले जातात."},
    "impersonation_advance": {"en": "Scammers pretend to be a relative in trouble, a bank 'fraud team' or a seller, and rush you to send money. Hang up and call the real person on the number you already have. A bank never asks you to move savings to a 'safe account'.",
                              "hi": "ठग किसी मुसीबत में फंसे रिश्तेदार, बैंक की 'फ्रॉड टीम' या विक्रेता बनकर जल्दी पैसे भेजने को कहते हैं। फोन काटें और अपने पास मौजूद असली नंबर पर उस व्यक्ति को कॉल करें। बैंक कभी बचत को 'सेफ अकाउंट' में भेजने को नहीं कहता।",
                              "mr": "फसवणूक करणारे संकटातील नातेवाईक, बँकेची 'फ्रॉड टीम' किंवा विक्रेता बनून घाईने पैसे पाठवायला सांगतात. फोन कट करा आणि तुमच्याकडे असलेल्या खऱ्या नंबरवर त्या व्यक्तीला कॉल करा. बँक कधीही बचत 'सेफ अकाउंट'मध्ये हलवायला सांगत नाही."},
    "bank_alert": {"en": "This looks like a normal transaction alert from a bank. It contains no link and asks for nothing. If you did not make this transaction, call the number on the back of your card.",
                   "hi": "यह बैंक का सामान्य लेन-देन संदेश लगता है। इसमें कोई लिंक नहीं है और कुछ मांगा नहीं गया। अगर यह लेन-देन आपने नहीं किया, तो कार्ड के पीछे दिए नंबर पर कॉल करें।",
                   "mr": "हा बँकेचा सामान्य व्यवहार संदेश वाटतो. त्यात लिंक नाही आणि काही मागितलेले नाही. हा व्यवहार तुम्ही केला नसेल तर कार्डच्या मागील नंबरवर कॉल करा."},
    "otp_notice": {"en": "This is a normal one-time password. It is only for you. Do not tell it to anyone, even if they say they are from the bank. If you did not request it, ignore it.",
                   "hi": "यह सामान्य वन-टाइम पासवर्ड है। यह सिर्फ आपके लिए है। बैंक वाला बनकर भी कोई मांगे तो न बताएं। आपने नहीं मांगा हो तो अनदेखा करें।",
                   "mr": "हा सामान्य वन-टाइम पासवर्ड आहे. तो फक्त तुमच्यासाठी आहे. बँकेचा असल्याचे सांगणाऱ्यालाही सांगू नका. तुम्ही मागितला नसेल तर दुर्लक्ष करा."},
    "bill_reminder": {"en": "This looks like a normal bill reminder. Pay only through the provider's official app, website or counter, not through links from unknown numbers.",
                      "hi": "यह सामान्य बिल अनुस्मारक लगता है। भुगतान सिर्फ कंपनी के आधिकारिक ऐप, वेबसाइट या काउंटर पर करें, अनजान नंबर के लिंक से नहीं।",
                      "mr": "हे सामान्य बिल स्मरणपत्र वाटते. भरणा फक्त कंपनीच्या अधिकृत ॲप, वेबसाइट किंवा काउंटरवर करा, अनोळखी नंबरच्या लिंकवर नाही."},
    "govt_notice": {"en": "This looks like a normal official notice. Check it only on the department's official website (ending in .gov.in), never through a link in the message.",
                    "hi": "यह सामान्य सरकारी सूचना लगती है। इसे सिर्फ विभाग की आधिकारिक वेबसाइट (.gov.in) पर जांचें, संदेश के लिंक से नहीं।",
                    "mr": "ही सामान्य सरकारी सूचना वाटते. ती फक्त विभागाच्या अधिकृत वेबसाइटवर (.gov.in) तपासा, मेसेजमधील लिंकवरून नाही."},
    "delivery_update": {"en": "This looks like a normal delivery update. Share a delivery PIN only with the person at your door, and track orders in the shop's own app.",
                        "hi": "यह सामान्य डिलीवरी अपडेट लगता है। डिलीवरी PIN सिर्फ दरवाज़े पर खड़े व्यक्ति को बताएं और ऑर्डर दुकान के अपने ऐप में ट्रैक करें।",
                        "mr": "हे सामान्य डिलिव्हरी अपडेट वाटते. डिलिव्हरी PIN फक्त दारावरील व्यक्तीला सांगा आणि ऑर्डर दुकानाच्या ॲपमध्येच ट्रॅक करा."},
    "general": {"en": "This looks like an ordinary personal message and does not match any known scam pattern.",
                "hi": "यह सामान्य निजी संदेश लगता है और किसी जानी-पहचानी ठगी से मेल नहीं खाता।",
                "mr": "हा सामान्य वैयक्तिक संदेश वाटतो आणि कोणत्याही ज्ञात फसवणुकीशी जुळत नाही."},
}

STEPS_SCAM = {
    "en": ["Do not click any link, call back the number, or install any app.", "Do not send money or share an OTP, PIN, CVV or Aadhaar photo.",
           "Call 1930 (national cyber-fraud helpline) at once if you already paid or shared anything.",
           "Report the message at sancharsaathi.gov.in (Chakshu) or cybercrime.gov.in.", "Tell a family member. Scammers want you to keep it secret."],
    "hi": ["कोई लिंक न खोलें, उस नंबर पर वापस कॉल न करें और कोई ऐप इंस्टॉल न करें।", "पैसे न भेजें और OTP, PIN, CVV या आधार की फोटो साझा न करें।",
           "अगर आप पैसे दे चुके हैं या कुछ बता चुके हैं तो तुरंत 1930 (साइबर ठगी हेल्पलाइन) पर कॉल करें।",
           "संदेश की शिकायत sancharsaathi.gov.in (चक्षु) या cybercrime.gov.in पर करें।", "परिवार के किसी सदस्य को बताएं। ठग चाहते हैं कि आप इसे गुप्त रखें।"],
    "mr": ["कोणतीही लिंक उघडू नका, त्या नंबरवर परत कॉल करू नका आणि कोणतेही ॲप इन्स्टॉल करू नका.", "पैसे पाठवू नका आणि OTP, PIN, CVV किंवा आधारचा फोटो शेअर करू नका.",
           "तुम्ही पैसे दिले असतील किंवा काही सांगितले असेल तर लगेच 1930 (सायबर फसवणूक हेल्पलाइन) वर कॉल करा.",
           "मेसेजची तक्रार sancharsaathi.gov.in (चक्षु) किंवा cybercrime.gov.in वर करा.", "कुटुंबातील कोणाला तरी सांगा. तुम्ही हे गुप्त ठेवावे अशी फसवणूक करणाऱ्यांची इच्छा असते."],
}
STEPS_SUSPICIOUS = {
    "en": ["Do not click the link or reply yet.", "Check the same information in the company's or department's official app or website, typed by you.",
           "Call the official helpline printed on your card or bill, not a number in the message.", "If unsure, show it to a family member or call 1930."],
    "hi": ["अभी लिंक न खोलें और जवाब न दें।", "वही जानकारी कंपनी या विभाग के आधिकारिक ऐप या वेबसाइट पर खुद टाइप करके जांचें।",
           "कार्ड या बिल पर छपे आधिकारिक हेल्पलाइन नंबर पर कॉल करें, संदेश वाले नंबर पर नहीं।", "संदेह हो तो परिवार के किसी सदस्य को दिखाएं या 1930 पर कॉल करें।"],
    "mr": ["आत्ता लिंक उघडू नका आणि उत्तर देऊ नका.", "तीच माहिती कंपनी किंवा विभागाच्या अधिकृत ॲप किंवा वेबसाइटवर स्वतः टाइप करून तपासा.",
           "कार्ड किंवा बिलावर छापलेल्या अधिकृत हेल्पलाइनवर कॉल करा, मेसेजमधील नंबरवर नाही.", "शंका असल्यास कुटुंबातील कोणाला दाखवा किंवा 1930 वर कॉल करा."],
}
STEPS_GENUINE = {
    "en": ["No scam signs found. Still, never share an OTP or PIN with anyone.", "If you were not expecting it, check in the official app instead of any link."],
    "hi": ["ठगी के कोई संकेत नहीं मिले। फिर भी OTP या PIN किसी को न बताएं।", "अगर आपको इसकी उम्मीद नहीं थी तो किसी लिंक की बजाय आधिकारिक ऐप में जांचें।"],
    "mr": ["फसवणुकीची कोणतीही चिन्हे आढळली नाहीत. तरीही OTP किंवा PIN कोणालाही सांगू नका.", "तुम्हाला याची अपेक्षा नव्हती तर लिंकऐवजी अधिकृत ॲपमध्ये तपासा."],
}

VERDICT = {
    "scam": {"en": "Very likely a scam", "hi": "लगभग निश्चित ठगी", "mr": "जवळजवळ निश्चित फसवणूक"},
    "suspicious": {"en": "Suspicious: be careful", "hi": "संदिग्ध: सावधान रहें", "mr": "संशयास्पद: सावध रहा"},
    "genuine": {"en": "Looks genuine", "hi": "असली लगता है", "mr": "खरे वाटते"},
}

SIGNALS = {
    "asks_secret": {"en": "Asks for an OTP, PIN, CVV or password", "hi": "OTP, PIN, CVV या पासवर्ड मांगता है", "mr": "OTP, PIN, CVV किंवा पासवर्ड मागतो"},
    "asks_money": {"en": "Asks you to pay a fee, deposit or 'charge' first", "hi": "पहले फीस, डिपॉज़िट या 'चार्ज' भरने को कहता है", "mr": "आधी फी, डिपॉझिट किंवा 'चार्ज' भरायला सांगतो"},
    "urgency": {"en": "Creates panic with a deadline", "hi": "समय-सीमा देकर घबराहट पैदा करता है", "mr": "मुदत देऊन घबराट निर्माण करतो"},
    "threat": {"en": "Threatens arrest, blocking or disconnection", "hi": "गिरफ्तारी, खाता बंद या कनेक्शन कटने की धमकी देता है", "mr": "अटक, खाते बंद किंवा कनेक्शन तोडण्याची धमकी देतो"},
    "secrecy": {"en": "Tells you not to inform anyone", "hi": "किसी को न बताने को कहता है", "mr": "कोणालाही न सांगण्यास सांगतो"},
    "remote_app": {"en": "Asks you to install a remote-access or unknown app", "hi": "रिमोट-एक्सेस या अनजान ऐप इंस्टॉल करने को कहता है", "mr": "रिमोट-ॲक्सेस किंवा अनोळखी ॲप इन्स्टॉल करायला सांगतो"},
    "short_link": {"en": "Contains a shortened link that hides the real site", "hi": "छोटा लिंक है जो असली साइट छुपाता है", "mr": "लहान लिंक आहे जी खरी साइट लपवते"},
    "fake_domain": {"en": "Link looks like a bank or government site but is not official", "hi": "लिंक बैंक या सरकारी साइट जैसा दिखता है पर आधिकारिक नहीं है", "mr": "लिंक बँक किंवा सरकारी साइटसारखी दिसते पण अधिकृत नाही"},
    "personal_number": {"en": "Asks you to call or pay a personal mobile number", "hi": "निजी मोबाइल नंबर पर कॉल या भुगतान करने को कहता है", "mr": "वैयक्तिक मोबाइल नंबरवर कॉल किंवा भरणा करायला सांगतो"},
    "too_good": {"en": "Promises money or prizes you did not ask for", "hi": "बिना मांगे पैसे या इनाम का वादा करता है", "mr": "न मागता पैसे किंवा बक्षिसाचे आश्वासन देतो"},
    "pay_first": {"en": "Asks you to pay or send money first, by UPI or to a personal number", "hi": "पहले UPI या निजी नंबर पर पैसे भेजने को कहता है", "mr": "आधी UPI किंवा वैयक्तिक नंबरवर पैसे पाठवायला सांगतो"},
    "official_channel": {"en": "Points you to the official app, website or store (a good sign)", "hi": "आधिकारिक ऐप, वेबसाइट या स्टोर पर जाने को कहता है (अच्छा संकेत)", "mr": "अधिकृत ॲप, वेबसाइट किंवा स्टोअरकडे जायला सांगतो (चांगले चिन्ह)"},
    "no_share": {"en": "Warns you NOT to share the code (a good sign)", "hi": "कोड किसी को न बताने की चेतावनी देता है (अच्छा संकेत)", "mr": "कोड कोणालाही न सांगण्याची सूचना देतो (चांगले चिन्ह)"},
    "official_link": {"en": "Link is an official .gov.in / known bank domain", "hi": "लिंक आधिकारिक .gov.in / जानी-मानी बैंक साइट है", "mr": "लिंक अधिकृत .gov.in / ओळखीच्या बँकेची साइट आहे"},
}

HELPLINES = [
    {"name": "National Cyber-Fraud Helpline", "number": "1930", "note": "Call immediately if money was lost (the first hour matters most)", "url": "https://cybercrime.gov.in"},
    {"name": "Report on Chakshu (Sanchar Saathi)", "number": "", "note": "Report suspicious calls, SMS and WhatsApp", "url": "https://sancharsaathi.gov.in"},
    {"name": "National Consumer Helpline", "number": "1915", "note": "Refunds and consumer complaints", "url": "https://consumerhelpline.gov.in"},
    {"name": "Emergency (police)", "number": "112", "note": "If you feel physically threatened", "url": ""},
    {"name": "Women Helpline", "number": "181", "note": "Blackmail and harassment", "url": ""},
]

OFFICIAL_SUFFIXES = (".gov.in", ".nic.in", ".sbi.co.in", ".onlinesbi.sbi", ".hdfcbank.com", ".icicibank.com", ".axisbank.com", ".pnbindia.in",
                     ".bankofbaroda.in", ".kotak.com", ".npci.org.in", ".uidai.gov.in", ".incometax.gov.in", ".indiapost.gov.in", ".amazon.in",
                     ".flipkart.com", ".irctc.co.in", ".paytm.com", ".phonepe.com", ".licindia.in", ".rbi.org.in", ".airtel.in", ".jio.com", ".sancharsaathi.gov.in", ".cybercrime.gov.in")
BRAND_WORDS = ("sbi", "hdfc", "icici", "axis", "pnb", "kotak", "paytm", "phonepe", "aadhaar", "aadhar", "uidai", "incometax", "irctc", "bank", "kyc",
               "gov", "india", "customs", "refund", "bijli", "electric", "bescom", "msedcl")
SHORTENERS = ("bit.ly", "tinyurl.com", "is.gd", "t.co", "rb.gy", "cutt.ly", "goo.gl", "ow.ly", "shorturl.at", "tiny.cc")
RISKY_TLDS = (".xyz", ".top", ".club", ".cc", ".info", ".co", ".site", ".online", ".icu", ".buzz", ".live", ".click", ".link", ".win", ".vip")
