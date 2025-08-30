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
	1. Go to https://www.linkedin.com and click on the jobs icon to access the jobs site. If prompted to log in, use the following credentials:
	   Email: {email}
	   Password: {password}
	   If prompted for OTP, use the gmail_find_otp function to retrieve the OTP from your Gmail inbox.
	2. Search for "Software Engineer" jobs in "Bangalore,Karnataka,India" in the search bar.
    3. Filter results to show only "Remote" jobs.
	4. Apply to the first 3 jobs that match the criteria using the "Easy Apply" option.
    5. For each application, fill out the required fields with placeholder information and submit.
    6. After applying, extract the job titles,companies, applied date of the applied jobs in accordance to the f{JobPost} schema.
    7. For the current date, use this {datetime.now().date()}
    8. For application status, use one of the following: "applied", "interviewing", "rejected", "offer_received".
    9. Compile the jobs into a list following the f{Jobs} schema and print the JSON output.
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