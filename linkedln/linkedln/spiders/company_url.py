import scrapy
import json
from ..utils import utils, COOKIE_STRING
import string
from linkedin_api import Linkedin
from linkedin_api.client import Client
import requests
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class LinkedlnCompanySpider(scrapy.Spider):


    name = "company_url"

    def start_requests(self):
        
        yield SeleniumRequest(
            url      = "https://www.linkedin.com",
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": utils.random_user_agent()
            },
            callback  = self.get_login_function,
            wait_time = 5,
        )

    def get_login_function(self, response, **kwargs):
        
        driver = response.meta['driver']
        email_field = driver.find_element(By.ID, 'session_key')
        email_field.send_keys('thanhnghi090500@gmail.com')

        password_field = driver.find_element(By.ID, 'session_password')
        password_field.send_keys('3Vc;4Pi@1Xe$')

        submit_button = driver.find_element(By.XPATH, '//form/div[2]/button')
        submit_button.click()

        cookies = driver.get_cookies()

        csrf_token =  next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), None)['value'].replace('"',"")

        desired_cookies = { cookie['name'] : cookie['value'].replace('"',"") for cookie in cookies }

       
        for i in range(0, 991, 10):
            yield scrapy.Request(
                url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{i},origin:SWITCH_SEARCH_VERTICAL,query:(keywords:a,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
                headers = {
                    'accept': 'application/vnd.linkedin.normalized+json+2.1',
                    'accept-encoding': 'gzip, deflate, br',
                    'csrf-token': csrf_token,
                    'user-agent': utils.random_user_agent()
                },
                cookies = desired_cookies,
                callback = self.get_company_urls,
            )
        

    def get_company_urls(self, response):

        data = response.json()
    
        company_urls =  [ data_url for data_url in data['included'] if "template" in data_url  ]
        for company_url in company_urls:
            yield {
                'keyword': 'a',
                'url': company_url['navigationUrl']
            }
        


    def get_company_details(self, response):
        return

    def parse(self, response):
        pass
