import scrapy
import json
from ..utils import utils
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import datetime
from urllib.parse import quote
from selenium.common.exceptions import NoSuchElementException


class ProfileUrlSpider(scrapy.Spider):

    name = "people_url"
    count = 0

    def handle_error(self, failure):

        failed_url = failure.request.url
        now = datetime.datetime.now()
        log_entry = f"Processed Failed With: {failed_url}, Datetime: {now}\n"

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

        
        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{self.count},origin:FACETED_SEARCH,query:(keywords:a,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:currentCompany,value:List(1035,1441,11864448,1337,5597)),(key:geoUrn,value:List(103644278)),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            cookies = desired_cookies,
            callback = self.get_people_urls,
            errback = self.handle_error,
            meta = {
                'cookies': desired_cookies,
                'csrf_token': csrf_token
            }
        ) 

    def get_people_urls(self, response):

        data = response.json()
        cookies      = response.meta['cookies']
        csrf_token   = response.meta['csrf_token']


        people_urls = [ data_url for data_url in data['included'] if "template" in data_url ]
        for people_url in people_urls:

            
            navigate_url  = people_url['navigationUrl']

            if not navigate_url: continue
            if "https://www.linkedin.com/search/results/people" in navigate_url: continue
            
            linkedin_url, query_string = navigate_url.split('?')
            mini_profile_key, query_params = query_string.split('=')
            mini_profile_urn, mini_profile = query_params.split('_miniProfile')
            
            yield {
                'linkedin_url': linkedin_url,
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
            }

        if self.count >= 1000: return
        self.count += 10  
        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{self.count},origin:FACETED_SEARCH,query:(keywords:a,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:currentCompany,value:List(1035,1441,11864448,1337,5597)),(key:geoUrn,value:List(103644278)),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            cookies = cookies,
            callback = self.get_people_urls,
            errback = self.handle_error,
            meta = {
                'cookies': cookies,
                'csrf_token': csrf_token
            }
        ) 


    def get_people_first_details(self, response):
        return
    
    def get_people_second_details(self, response):
        return
    
    def get_people_third_details(self, response):
        return