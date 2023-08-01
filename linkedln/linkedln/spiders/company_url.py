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

    LINKEDIN_BASE_URL = "https://www.linkedin.com"
    API_BASE_URL = f"{LINKEDIN_BASE_URL}/voyager/api"
    REQUEST_HEADERS = {
        "user-agent": " ".join(
            [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5)",
                "AppleWebKit/537.36 (KHTML, like Gecko)",
                "Chrome/83.0.4103.116 Safari/537.36",
            ]
        ),
        # "accept": "application/vnd.linkedin.normalized+json+2.1",
        "accept-language": "en-AU,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
        "x-li-lang": "en_US",
        "x-restli-protocol-version": "2.0.0",
        # "x-li-track": '{"clientVersion":"1.2.6216","osName":"web","timezoneOffset":10,"deviceFormFactor":"DESKTOP","mpName":"voyager-web"}',
    }
    AUTH_REQUEST_HEADERS = {
        "X-Li-User-Agent": "LIAuthLibrary:3.2.4 \
                            com.linkedin.LinkedIn:8.8.1 \
                            iPhone:8.3",
        "User-Agent": "LinkedIn/8.8.1 CFNetwork/711.3.18 Darwin/14.0.0",
        "X-User-Language": "en",
        "X-User-Locale": "en_US",
        "Accept-Language": "en-us",
    }
    
    
    def _request_session_cookies(self):
       
        self.logger.debug("Requesting new cookies.")

        res = requests.get(
            f"{self.LINKEDIN_BASE_URL}/uas/authenticate",
            headers=self.AUTH_REQUEST_HEADERS,
            #proxies=self.proxies,
        )

        return res.cookies

    def _set_session_cookies(self, cookies):

        self.session.cookies = cookies
        self.session.headers["csrf-token"] = self.session.cookies["JSESSIONID"].strip(
            '"'
        )


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

       

        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:0,origin:SWITCH_SEARCH_VERTICAL,query:(keywords:a,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
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
        with open('index.json', 'w') as f:
            f.write(str(data))
        # company_urls =  [ "template" in data_url for data_url in data['url']['included']  ]
        # for company_url in company_urls:
        #     yield {
        #         'url': company_url['navigationUrl']
        #     }
        


    def get_company_details(self, response):
        return

    def parse(self, response):
        pass
