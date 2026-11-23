# Deploy Kagaz Saathi to AWS (about 20 minutes, Free Tier)

Everything below is done by **you** in your own account: AWS needs your identity, phone and card to open an account,
and nobody else should do that for you. The code, template and tests are ready; nothing here was deployed by Claude.

## 0. One-time setup (required by the hackathon)
1. Create your **AWS Builder Center** profile at builder.aws.com and claim your alias.
2. Verify your student status there (SheerID). The organisers recommend doing this by **27 Nov**.
3. Create an AWS account on the **Free plan** (sign in with the same Builder ID).
4. In the console: **Billing -> Budgets -> Create budget** (a 5 USD monthly cost budget with an email alert).
5. Install the AWS CLI and AWS SAM CLI, then run `aws configure` (use an IAM user or `aws login`; never paste keys into a chat).

## 1. Build the package
```powershell
python infra/build.py          # assembles build/ (3.6 MB)
```

## 2. Deploy
```powershell
cd infra
sam deploy --template-file template.yaml --stack-name kagaz-saathi --region ap-southeast-2 `
  --capabilities CAPABILITY_IAM --resolve-s3 --parameter-overrides EnableTextract=0
```
`sam deploy` prints **AppUrl**. That is your live prototype URL. Open it and click **Try the live demo**.

Optional: real email alerts to family. In the console open **Amazon SES -> Verified identities**, verify one email address,
then redeploy with `--parameter-overrides AlertFromEmail=you@example.com`. (New SES accounts are in the sandbox, so recipients must be verified too.)

## 3. Check it works
- `AppUrl/` shows the landing page; **Try it now** gives a verdict without signing in.
- Create an account, check a message, add a family member, press **Alert family**.
- Upload a photo: it is read in your browser (Tesseract.js).
- CloudWatch Logs -> `/aws/lambda/kagaz-saathi-KagazFunction-...` shows any error.

## 4. Keep it live through Demo Day (17 Dec)
- The Free plan lasts up to 6 months or until credits run out; keep an eye on Billing.
- Lambda + DynamoDB on-demand cost nothing at demo traffic.
- Do not delete the stack until after Demo Day. To remove everything later: `sam delete --stack-name kagaz-saathi`.

## What each AWS service does here
| Service | Used for |
|---|---|
| AWS Lambda + Function URL | The whole app (pages, static files and the JSON API) in one function |
| Amazon DynamoDB | Accounts, sessions (TTL), checks, family and alert outbox (one table) |
| Amazon SES (optional) | Delivers family alerts to email contacts |
| Amazon CloudWatch | Logs and metrics |

Tested locally with `moto` (a mock of AWS): `python -m pytest tests/test_aws.py`, and then against the real deployment (see below).

## What really happened on a real Free-plan account (23 Nov 2026)
- A new Free-plan account is tied to **Sydney (ap-southeast-2)**; other regions need a paid upgrade. We deployed there.
- **Amazon Textract, Translate and Comprehend are blocked** by an organisation policy on Free-plan accounts, so photos are read in the browser instead. Amazon Polly works but has no Hindi voice in Sydney, so read-aloud uses the browser's voices.
- **Lambda Function URL, DynamoDB, CloudFormation/SAM and CloudWatch work.** Amazon SES responds (200 emails a day, sandbox) but needs a verified sender before it will send.
- All 10 browser-test steps pass against the live deployment.
