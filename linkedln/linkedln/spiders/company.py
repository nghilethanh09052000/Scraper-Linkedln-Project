import scrapy
import json
from ..utils import utils, COOKIE_STRING

class LinkedlnCompanySpider(scrapy.Spider):

    name = "company"
    headers = {
                'Accept': 'application/vnd.linkedin.normalized+json+2.1',
                'Cookie': COOKIE_STRING,
                'Csrf-Token': 'ajax:4783027849707025508',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'User-Agent': utils.random_user_agent()
            }
    offset = 0

    def start_requests(self):

        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{self.offset},origin:CLUSTER_EXPANSION,query:(keywords:company,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:resultType,value:List(COMPANIES))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
            headers = self.headers,
            method = 'GET',
            cookies = utils.cookie_parser(),
            callback = self.get_all_companies
        )
    
    def get_all_companies(self, response):

        item = {}
        json_response = json.loads(response['data'])

        yield {
            json_response
        }


        # yield scrapy.Request(
        #     url = '',
        #     headers = {

        #     },
        #     callback = self
        # )   

    def get_company_details(self, response):
        return

    def parse(self, response):
        pass
