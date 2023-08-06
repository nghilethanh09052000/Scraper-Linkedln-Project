import scrapy
import json
from ..utils import utils, COOKIE_STRING
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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
                return int(follower['followerCount'])

    def start_requests(self):
        
        yield SeleniumRequest(
            url      = "https://www.linkedin.com",
            # headers = {
            #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            #     "Accept-Encoding": "gzip, deflate, br",
            #     "Accept-Language": "en-US,en;q=0.9",
            #     "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Microsoft Edge";v="115", "Chromium";v="115"',
            #     "Sec-Ch-Ua-Mobile": "?0",
            #     "Sec-Ch-Ua-Platform": '"Windows"',
            #     "Sec-Fetch-Dest": "document",
            #     "Sec-Fetch-Mode": "navigate",
            #     "Sec-Fetch-Site": "none",
            #     "Sec-Fetch-User": "?1",
            #     "Upgrade-Insecure-Requests": "1",
            #     "User-Agent": utils.random_user_agent()
            # },
            callback  = self.get_login_function,
            wait_time = 5,
        )

    def get_login_function(self, response, **kwargs):
        
        driver = response.meta['driver']
        email_field = driver.find_element(By.XPATH, '//form/div[1]/div/div/div/input[@name="session_key"]')
        email_field.send_keys('thanhnghi591@gmail.com')

        password_field = driver.find_element(By.XPATH, '//form/div[1]/div/div/div/input[@name="session_password"]')
        password_field.send_keys('abcABC@123')

        submit_button = driver.find_element(By.XPATH, '//form/div[2]/button')
        submit_button.click()

        cookies = driver.get_cookies()

        csrf_token =  next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), None)['value'].replace('"',"")

        desired_cookies = { cookie['name'] : cookie['value'].replace('"',"") for cookie in cookies }

       
        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{str(self.count)},origin:SWITCH_SEARCH_VERTICAL,query:(keywords:a,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            cookies = desired_cookies,
            callback = self.get_company_urls,
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

            if not name: continue

            yield scrapy.Request(
                url = f"https://www.linkedin.com/voyager/api/graphql?variables=(universalName:{name})&&queryId=voyagerOrganizationDashCompanies.4fbcd4df2d3e37fcf3a4f5296be958b9",
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
                callback = self.get_company_details
            )

        if self.count >= 1000: return

        self.count+=10
        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{str(self.count)},origin:SWITCH_SEARCH_VERTICAL,query:(keywords:a,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            cookies = cookies,
            callback = self.get_company_urls,
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
       viewerPermissions = [ i for i in data['included'] if "viewerPermissions" in i ][0]

       name        = viewerPermissions.get('name')
       employee    = viewerPermissions.get('employeeCount')
       company_url = viewerPermissions.get('websiteUrl')
       phone       = viewerPermissions.get('phone')
       description = viewerPermissions.get('description').trim() if viewerPermissions.get('description') is not None else None
       tagline     = viewerPermissions.get('tagline')
       founded     = int(viewerPermissions.get('foundedOn')['year']) if viewerPermissions.get('foundedOn') is not None else None

       headquarter = viewerPermissions.get('headquarter')['address']
       country_code = headquarter.get('country')
       geographicArea = headquarter.get('geographicArea')
       city = headquarter.get('city')
       postal_code = headquarter.get('postalCode')
       line1 = headquarter.get('line1')
       line2 = headquarter.get('line2')
       
       industry = self.get_industry(industries, viewerPermissions.get('*industry')[0] )
       follower = self.get_followers(followers, viewerPermissions.get('*followingState'))



       yield {
           'name': name,
           'linkedin_url': linkedin_url,
           'industry': industry,
           'tagline': tagline,
           'phone': phone,
           'description': description,
           'company_url': company_url,
           'founded': founded,
           'linkedin_followers': int(follower),
           'employees': int(employee),
           'country_code': country_code,
           'geographicArea': geographicArea,
           'postal_code': postal_code,
           'city': city,
           'line1': line1,
           'line2': line2,
        }
   