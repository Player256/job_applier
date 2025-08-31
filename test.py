import os
import base64
import re
import asyncio
from datetime import datetime
from model import Jobs, JobPost
from dotenv import load_dotenv
load_dotenv()

from browser_use import Agent, BrowserProfile, Tools
from gmail_service import gmail_service

SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
"""

email = os.environ.get('USER_EMAIL')
password = os.environ.get('USER_PASSWORD')

tool = Tools()

@tool.action(description="Find latest email OTP code in Gmail")
def gmail_find_otp(q: str = 'in:inbox (subject:OTP OR subject:code OR subject:verification OR "one-time password") is:unread', pattern: str = r"\b(\d{4,8})\b", max_messages: int = 20) -> str:
    service = gmail_service()
    res = service.users().messages().list(userId="me", q=q, maxResults=max_messages).execute()
    messages = res.get("messages", [])
    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        snippet = msg.get("snippet", "")
        match = re.search(pattern, snippet)
        if match:
            return match.group(1)
        payload = msg.get("payload", {})
        parts = payload.get("parts", []) or []
        bodies = []
        if payload.get("body", {}).get("data"):
            bodies.append(payload["body"]["data"])
        for p in parts:
            if p.get("mimeType", "").startswith("text/") and p.get("body", {}).get("data"):
                bodies.append(p["body"]["data"])
        for b64 in bodies:
            data = base64.urlsafe_b64decode(b64.encode("utf-8")).decode("utf-8", errors="ignore")
            match = re.search(pattern, data)
            if match:
                return match.group(1)
    return ""



async def main():
	from browser_use import ChatGoogle

	llm = ChatGoogle(model='gemini-2.5-flash')

	browser_profile = BrowserProfile(
		minimum_wait_page_load_time=0.1,
		wait_between_actions=0.1,
		headless=False,
	)

	task = f"""
		1. Open https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4292948631 -> Log in with:
		Email: {email}, Password: {password}.
		If OTP required, use gmail_find_otp() to fetch from Gmail.

		2. Dont scroll or waste moving around, find thesearch bar. There are specifically two search bars one for job_title and another for location. In the search bar:
		- Job Title: "Machine Learning Intern"
		- Location: "Bangalore" (clear existing text first if any).
		- Run the search.

		3. Apply filters:
		- Job Type → Internship
		- Easy Apply → Enabled
		- Show results.

		4. For the first 3 results with "Easy Apply":
		- Open job → Click "Easy Apply"
		- Auto-fill form using:
			{{
			"First Name": "Dattatreya",
			"Last Name": "Varma",
			"Email": "{email}",
			"Phone": "9437772429",
			"City": "Bangalore",
			"State": "Karnataka",
			"Country": "India",
			"Zip Code": "560076",
			"Notice Period": "0",
			"Current CTC": "0",
			"Expected CTC": "10",
			"Experience in Python": "1",
			"Experience in Pytorch": "1",
			"Experience in Machine Learning": "1",
			"Experience in Deep Learning": "1"
			}}
		- Keep pre-filled fields unchanged.
		- If additional steps/questions appear → answer with placeholders or skip.
		- Click "Next" untill you get "Submit" and click "Submit".

		5. After applying, extract for each job:
		- title, company, applied date = {datetime.now().date()}, status = "applied".

		6. Save results in f{Jobs} schema and print JSON output.
"""


	agent = Agent(
		task=task,
		llm=llm,
		flash_mode=True,  
		browser_profile=browser_profile,
		extend_system_message=SPEED_OPTIMIZATION_PROMPT,
		output_model_schema=Jobs,
		tools=tool,
	)

	history = await agent.run()
	
	result = history.final_result()
 
	if result:
		print(result)
		parsed: Jobs = Jobs.model_validate_json(result)
		
		for job in parsed.jobs:
			print(f"Title: {job.job_title}, Company: {job.company}, Location: {job.location}, Date Applied: {job.date_applied}, Status: {job.application_status}")
	else:
		print("No result obtained from the agent.")
     
     


if __name__ == '__main__':
	asyncio.run(main())