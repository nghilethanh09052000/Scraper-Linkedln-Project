import scrapy
import json
from ..utils import utils
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import datetime
from urllib.parse import quote
from selenium.common.exceptions import NoSuchElementException


class LinkedlnCompanySpider(scrapy.Spider):


    name = "company_url"
    count = 0

    def get_industry(self, industries, company_industry):
        for industry in industries:
            if company_industry == industry['entityUrn']:
                return industry['name']
    
    def get_followers(self, followers, company_follower):
        for follower in followers:
            if company_follower == follower['entityUrn']:
                return int(follower['followerCount']) if type(follower['followerCount']) is str else follower['followerCount']
            
    def handle_error(self, failure):

        failed_url = failure.request.url
        now = datetime.datetime.now()
        log_entry = f"Processed Failed With: {failed_url}, Datetime: {now}\n, Keyword: {self.keyword}"

        with open(f'{self.keyword}_error_log.txt', 'a') as log_file:
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

        keyword = self.keyword
       
        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{str(self.count)},origin:SWITCH_SEARCH_VERTICAL,query:(keywords:{keyword},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            cookies = desired_cookies,
            callback = self.get_company_urls,
            errback = self.handle_error,
            meta = {
                'cookies': desired_cookies,
                'csrf_token': csrf_token
            }
        )
        
    def get_company_urls(self, response):

        data         = response.json()
        cookies      = response.meta['cookies']
        csrf_token   = response.meta['csrf_token']
        company_urls = [ data_url for data_url in data['included'] if "template" in data_url ]

        for company_url in company_urls:

            navigate_url = company_url['navigationUrl']
            name = navigate_url.split('/')[-2]
            encode_company = quote(name, safe='')

            yield scrapy.Request(
                url = f"https://www.linkedin.com/voyager/api/graphql?variables=(universalName:{encode_company})&&queryId=voyagerOrganizationDashCompanies.4fbcd4df2d3e37fcf3a4f5296be958b9",
                headers = {
                    'accept': 'application/vnd.linkedin.normalized+json+2.1',
                    'accept-encoding': 'gzip, deflate, br',
                    'csrf-token': csrf_token,
                    'user-agent': utils.random_user_agent()
                },
                cookies = cookies,
                meta = {
                    'url': navigate_url
                },
                callback = self.get_company_details,
                errback=self.handle_error
            )

        if self.count >= 1000: return

        now = datetime.datetime.now()
        log_entry = f"Processed item count: {self.count}, Datetime: {now}\n, Keyword: {self.keyword}"
        with open(f'{self.keyword}_companies_logs.txt', 'a') as log_file:
            log_file.write(log_entry)

        self.count += 10  

        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{str(self.count)},origin:SWITCH_SEARCH_VERTICAL,query:(keywords:{self.keyword},flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            cookies = cookies,
            callback = self.get_company_urls,
            errback=self.handle_error,
            meta = {
                'cookies': cookies,
                'csrf_token': csrf_token
            }
        )
                
    def get_company_details(self, response):
       
       linkedin_url = response.meta['url']
       data  = response.json()

       
       industries = [ i for i in data['included'] if "name" in i ]
       followers =  [ i for i in data['included'] if "followeeCount" in i ]
       viewerPermissions = [ i for i in data['included'] if "viewerPermissions" in i ]

       if not viewerPermissions : return

       viewerPermissions = viewerPermissions[0]

       name        = viewerPermissions.get('name')
       employee    = int(viewerPermissions.get('employeeCount')) if type(viewerPermissions.get('employeeCount')) is str else viewerPermissions.get('employeeCount')
       company_url = viewerPermissions.get('websiteUrl')
       phone       = viewerPermissions.get('phone')['number'] if viewerPermissions.get('phone') is not None else None
       tagline     = viewerPermissions.get('tagline')
       founded     = viewerPermissions.get('foundedOn')['year'] if viewerPermissions.get('foundedOn') is not None else None
       
       headquarter    = viewerPermissions.get('headquarter')['address'] if viewerPermissions.get('headquarter') is not None else {}
       country_code   = headquarter.get('country')
       geographicArea = headquarter.get('geographicArea')
       city           = headquarter.get('city')
       postal_code    = headquarter.get('postalCode')
       line1          = headquarter.get('line1')
       line2          = headquarter.get('line2')
       
       industry = self.get_industry(industries, viewerPermissions.get('*industry')[0] ) if viewerPermissions.get('*industry') is not None else None
       follower = self.get_followers(followers, viewerPermissions.get('*followingState')) if viewerPermissions.get('*followingState') is not None else None


       yield {
           'name': name,
           'linkedin_url': linkedin_url,
           'industry': industry,
           'tagline': tagline,
           'phone': phone,
           'company_url': company_url,
           'founded': founded,
           'linkedin_followers': follower,
           'employees': employee,
           'country_code': country_code,
           'geographicArea': geographicArea,
           'postal_code': postal_code,
           'city': city,
           'line1': line1,
           'line2': line2,
        }
   