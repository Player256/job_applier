import os
import asyncio
from datetime import datetime
from model import Jobs, JobPost
from dotenv import load_dotenv
load_dotenv()

from browser_use import Agent, BrowserProfile

SPEED_OPTIMIZATION_PROMPT = """
Speed optimization instructions:
- Be extremely concise and direct in your responses
- Get to the goal as quickly as possible
- Use multi-action sequences whenever possible to reduce steps
"""

email = os.environ.get('USER_EMAIL')
password = os.environ.get('USER_PASSWORD')


async def main():
	from browser_use import ChatGoogle

	llm = ChatGoogle(model='gemini-2.5-flash')

	browser_profile = BrowserProfile(
		minimum_wait_page_load_time=0.1,
		wait_between_actions=0.1,
		headless=False,
	)

	task = f"""
	1. Go to https://www.linkedin.com/jobs/. If prompted to log in, use the following credentials:
	   Email: {email}
	   Password: {password}
	2. Search for "Software Engineer" jobs in "Bangalore,Karnataka,India" in the search bar.
    3. Filter results to show only "Remote" jobs.
	4. Apply to the first 3 jobs that match the criteria using the "Easy Apply" option.
    5. For each application, fill out the required fields with placeholder information and submit.
    6. After applying, extract the job titles,companies, applied date of the applied jobs in accordance to the f{JobPost} schema.
    7. For the current date, use this {datetime.now().date()}
    7. Compile the jobs into a list following the f{Jobs} schema and print the JSON output.
	"""

	agent = Agent(
		task=task,
		llm=llm,
		flash_mode=True,  
		browser_profile=browser_profile,
		extend_system_message=SPEED_OPTIMIZATION_PROMPT,
		output_model_schema=Jobs,
	)

	history = await agent.run()
	
	result = history.final_result()
 
	if result:
		parsed: Jobs = Jobs.model_validate_json(result)
		
		for job in parsed:
			print(f"Title: {job.title}, Company: {job.company}, Location: {job.location}, Date Applied: {job.date_applied}, Status: {job.application_status}")
	else:
		print("No result obtained from the agent.")
     
     


if __name__ == '__main__':
	asyncio.run(main())