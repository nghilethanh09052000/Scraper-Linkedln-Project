import scrapy
import json
from ..utils import utils
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import datetime
from urllib.parse import quote
from selenium.common.exceptions import NoSuchElementException


class JobSpider(scrapy.Spider):

    name = "job"
    start = 25

    def handle_error(self, failure):

        failed_url = failure.request.url
        now = datetime.datetime.now()
        log_entry = f" Datetime: {now}\n, {failed_url}"

        with open(f'error_log.txt', 'a') as log_file:
            log_file.write(log_entry)

    def start_requests(self):
        yield SeleniumRequest(
            url      = "https://www.linkedin.com",
            callback  = self.get_login_function,
            wait_time = 5,
        )
    
    def get_login_function(self, response, **kwargs):
        
        driver = response.meta['driver']

        try:
            email_field = driver.find_element(By.XPATH, '//form/div[1]/div/div/div/input[@name="session_key"]')
        except NoSuchElementException:
            driver.refresh()

        email_field = driver.find_element(By.XPATH, '//form/div[1]/div/div/div/input[@name="session_key"]')
        email_field.send_keys(self.settings.get('LINKEDIN_USERNAME'))

        password_field = driver.find_element(By.XPATH, '//form/div[1]/div/div/div/input[@name="session_password"]')
        password_field.send_keys(self.settings.get('LINKEDIN_PASSWORD'))

        submit_button = driver.find_element(By.XPATH, '//form/div[2]/button')
        submit_button.click()

        cookies = driver.get_cookies()

        csrf_token =  next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), None)['value'].replace('"',"")

        desired_cookies = { cookie['name'] : cookie['value'].replace('"',"") for cookie in cookies }

        #keyword = self.keyword if self.keyword else ''
       
        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-170&count=25&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_SEARCH_BUTTON,keywords:frontend,locationUnion:(geoId:103644278),spellCorrectionEnabled:true)&start={str(self.start)}',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            cookies = desired_cookies,
            callback = self.get_all_jobs,
            errback = self.handle_error,
            meta = {
                'cookies': desired_cookies,
                'csrf_token': csrf_token
            }
        )
    
    def get_all_jobs(self, response):

        data         = response.json()
        cookies      = response.meta['cookies']
        csrf_token   = response.meta['csrf_token']

        page = data['data']['paging']['total']
        metadata = data['data']['metadata'] if data.get('data') else {}
        job_card_queries = metadata['jobCardPrefetchQueries'] 
        if not job_card_queries: return

        job_cards = job_card_queries[0]['prefetchJobPostingCard']
        for key in job_cards:
            url_id = int(key.split("(")[1].split(")")[0].split(",")[0])
            yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/jobs/jobPostings/{str(url_id)}?decorationId=com.linkedin.voyager.deco.jobs.web.shared.WebFullJobPosting-65&topN=1&topNRequestedFlavors=List(TOP_APPLICANT,IN_NETWORK,COMPANY_RECRUIT,SCHOOL_RECRUIT,HIDDEN_GEM,ACTIVELY_HIRING_COMPANY)',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            #cookies = cookies,
            callback = self.get_job_details,
            errback = self.handle_error,
            meta = {
                'cookies': cookies,
                'csrf_token': csrf_token
            }
        )
    
        if self.start < page:
            self.start+=25
            yield scrapy.Request(
                url = f'https://www.linkedin.com/voyager/api/voyagerJobsDashJobCards?decorationId=com.linkedin.voyager.dash.deco.jobs.search.JobSearchCardsCollection-170&count=25&q=jobSearch&query=(origin:JOB_SEARCH_PAGE_SEARCH_BUTTON,keywords:frontend,locationUnion:(geoId:103644278),spellCorrectionEnabled:true)&start={str(self.start)}',
                headers = {
                    'accept': 'application/vnd.linkedin.normalized+json+2.1',
                    'accept-encoding': 'gzip, deflate, br',
                    'csrf-token': csrf_token,
                    'user-agent': utils.random_user_agent()
                },
                cookies = cookies,
                callback = self.get_all_jobs,
                errback = self.handle_error,
                meta = {
                    'cookies': cookies,
                    'csrf_token': csrf_token
                }
            )

    def get_job_details(self, response):

        init_data = response.json()

        data = init_data['data']
        included = init_data['included']

        company = next( (i for i in included if i.get('description') ), None )

        title = data.get('title')
        posting_url = data.get('jobPostingUrl')
        applies = data.get('applies')
        employment_type = data.get('formattedEmploymentStatus')
        description = data.get('description')['text'] if data.get('description') else None
        views = data.get('views')
        experience_level = data.get('formattedExperienceLevel')
        is_remoted = data.get('workRemoteAllowed')
        expire_at = data.get('expireAt')

        company_name = company.get('name')
        company_about = company.get('description')
        company_linkedin_followers = next( (i['followerCount'] for i in included if company.get('*followingInfo') == i.get('entityUrn')), '')
        company_linkedin_staff = company.get('staffCount')
        company_linkedin_url = company.get('url')
        company_industries = company.get('industries')[0] if company.get('industries') else None


        yield {
            'title': title,
            'posting_url': posting_url,
            'applies': applies,
            'employment_type': employment_type,
            'description': description,
            'views': views,
            'experience_level': experience_level,
            'is_remoted': is_remoted,
            'expire_at': expire_at,
            'company_name': company_name,
            'company_about': company_about,
            'company_linkedin_followers':company_linkedin_followers,
            'company_linkedin_staff': company_linkedin_staff,
            'company_linkedin_url': company_linkedin_url,
            'company_industries': company_industries
        }

