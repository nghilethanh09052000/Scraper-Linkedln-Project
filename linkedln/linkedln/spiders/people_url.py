import scrapy
import json
from ..utils import utils
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
import datetime
from urllib.parse import quote
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import quote
import re

class ProfileUrlSpider(scrapy.Spider):

    name = "people_url"
    count = 0

    def handle_error(self, failure):

        failed_url = failure.request.url
        now = datetime.datetime.now()
        log_entry = f"Processed Failed With: {failed_url}, Datetime: {now}\n"

        with open(f'error_log.txt', 'a') as log_file:
            log_file.write(log_entry)

    def format_people_categories(self, type, includes):
        categories = [
            'EXPERIENCE', 
            'EDUCATION', 
            'VOLUNTEERING', 
            'LANGUAGES',
            'SKILLS', 
            'ORGANIZATIONS', 
            'HONORS',
            'CERTIFICATIONS'
        ]
        data = []
        if  type in categories: 
            for include in includes:
                elements = include['components']['elements']
                for element in elements:
                    if element['components']['entityComponent']:

                        entity = element['components']['entityComponent']

                        first_value = entity['subtitle']['text'] if entity['subtitle'] else None
                        second_value = entity['titleV2']['text']['text']
                        third_value = entity['image']['actionTarget'] if entity['image'] else entity['textActionTarget']
                        fourth_value = entity['caption']['text'] if entity['caption'] else None
                        fifth_value = entity['supplementaryInfo']['text'] if entity['supplementaryInfo'] else None
                                    
                        data.append({
                            'first_key'  : first_value,
                            'second_key' : second_value,
                            'third_key'  : third_value,
                            'fourth_key' : fourth_value,
                            'fifth_key'  : fifth_value
                        })

        return data if data else []

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

        cookies_string = driver.get_cookies()

        csrf_token =  next((cookie for cookie in cookies_string if cookie['name'] == 'JSESSIONID'), None)['value'].replace('"',"")
        cookies = { cookie['name'] : cookie['value'].replace('"',"") for cookie in cookies_string }

        
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

    def get_people_urls(self, response):

        data = response.json()
        cookies = response.meta['cookies']
        csrf_token = response.meta['csrf_token']

        people_urls = [ data_url for data_url in data['included'] if "template" in data_url ]
        for people_url in people_urls:
        
            navigate_url  = people_url['navigationUrl'] # https://www.linkedin.com/in/thuyngas?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAAADGfg8BJyDI6qpbCXco6cnpia9eKgeoOwU

            if not navigate_url or "https://www.linkedin.com/search/results/people" in navigate_url: continue
            
            linkedin_url, query_string = navigate_url.split('?') # 
            _, query_params = query_string.split('=')
            mini_profile_urn, mini_profile = query_params.split('_miniProfile')
            user_name_url = quote(linkedin_url.split('/')[-1], safe='')

           
            yield scrapy.Request(
                url = f'https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={user_name_url}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.WebTopCardCore-20',
                headers = {
                    'accept': 'application/vnd.linkedin.normalized+json+2.1',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.9',
                    'csrf-token': csrf_token,
                    'user-agent': utils.random_user_agent()
                },
                #cookies = cookies,
                callback = self.get_basic_info,
                errback = self.handle_error,
                meta = {
                    'linkedin_url': linkedin_url,
                    'user_name_url': user_name_url,
                    'mini_profile_urn': mini_profile_urn,
                    'mini_profile': mini_profile,
                    'cookies': cookies,
                    'csrf_token': csrf_token
                }
            )


        if self.count >= 1000: return
        self.count += 10  
        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?variables=(start:{self.count},origin:FACETED_SEARCH,query:(keywords:a,flagshipSearchIntent:SEARCH_SRP,queryParameters:List((key:currentCompany,value:List(1035,1441,11864448,1337,5597)),(key:geoUrn,value:List(103644278)),(key:resultType,value:List(PEOPLE))),includeFiltersInResponse:false))&&queryId=voyagerSearchDashClusters.a789a8e572711844816fa31872de1e2f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent':  utils.random_user_agent()
            },
            cookies = cookies,
            callback = self.get_people_urls,
            errback = self.handle_error,
            meta = {
                'cookies': cookies,
                'csrf_token': csrf_token
            }
        ) 

    def get_basic_info(self, response): # Geographic and basic information

        item = {}
        csrf_token       = response.meta['csrf_token']
        linkedin_url     = response.meta['linkedin_url']
        user_name_url    = response.meta['user_name_url']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        cookies          = response.meta['cookies']
        data             = response.json()

        [user_info]  = [ i for i in data['included'] if 'birthDateOn' in i ]
        country_info = [ i for i in data['included'] if 'countryUrn' in i ]

        #if not user_info: return

        first_name = user_info.get('firstName')
        last_name  = user_info.get('lastName')
        headline   = user_info.get('headline')
        location   = user_info.get('geoLocation')['*geo'] if user_info.get('geoLocation') is not None else None
        
        if country_info and location:
            location = next( ( i['defaultLocalizedName'] for i in country_info if i.get('entityUrn') == location ), '')
        
        item = { 
            **item,
            'linkdin_url': linkedin_url,
            'first_name' : first_name,
            'last_name'  : last_name,
            'headline'   : headline,
            'location'   : location
        }

        yield scrapy.Request(
                url = f'https://www.linkedin.com/voyager/api/identity/dash/profiles?q=memberIdentity&memberIdentity={user_name_url}&decorationId=com.linkedin.voyager.dash.deco.identity.profile.TopCardSupplementary-131',
                headers = {
                    'accept': 'application/vnd.linkedin.normalized+json+2.1',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.9',
                    'csrf-token': csrf_token,
                    'user-agent': utils.random_user_agent()
                },
                callback = self.get_followers,
                errback = self.handle_error,
                meta = {
                    'user_name_url': user_name_url,
                    'mini_profile_urn': mini_profile_urn,
                    'mini_profile': mini_profile,
                    'cookies': cookies,
                    'csrf_token': csrf_token,
                    'item' : item
                }
            )
        
    def get_followers(self, response): # Follower Count

        csrf_token       = response.meta['csrf_token']
        cookies          = response.meta['cookies']
        user_name_url    = response.meta['user_name_url']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json()

        followers =  next( ( i['followerCount'] for i in data['included'] if 'followerCount' in i ) , None)

        
        item = {
            **item,
            'followers': int(followers) if followers else followers
        }

        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(memberIdentity:{user_name_url})&&queryId=voyagerIdentityDashProfiles.84cab0be7183be5d0b8e79cd7d5ffb7b',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            callback = self.get_contact_info,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'csrf_token': csrf_token,
                'cookies': cookies,
                'item' : item
            }
        )
    
    def get_contact_info(self, response): # Email | Facebook | Instagram | Twitter | Birthday

        csrf_token       = response.meta['csrf_token']
        cookies          = response.meta['cookies']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json()

        [contact_info] =  [ i for i in data['included'] if 'birthDateOn' in i ]

        birthday = {
            'month': contact_info.get('birthDateOn').get('month'),
            'day'  : contact_info.get('birthDateOn').get('day'),
            'year' : contact_info.get('birthDateOn').get('year'),
        } if contact_info.get('birthDateOn') else None
        
        websites = [ { 'url': i.get('url'), 'category': i.get('category'), 'label': i.get('label') } for i in contact_info.get('websites') ] if contact_info.get('websites') else None
        
        email = contact_info.get('emailAddress').get('emailAddress') if contact_info.get('emailAddress') else None

        twitter = None
        twitterHandles = contact_info.get('twitterHandles')
        if twitterHandles:
            twitter = twitterHandles[0].get('name')
            twitter = 'https://twitter.com/' + twitter
        
        phones  = contact_info.get('phoneNumbers')
        address = contact_info.get('address')

        item = {
            **item,
            'birthday': birthday,
            'websites': websites,
            'email'   : email,
            'twitter' : twitter,
            'phones'  : phones,
            'address' : address
        }
 
        yield scrapy.Request(
            url = f'https://www.linkedin.com/voyager/api/graphql?includeWebMetadata=true&variables=(profileUrn:{mini_profile_urn}d_profile{mini_profile})&&queryId=voyagerIdentityDashProfileCards.6ac5b932812d02137a06a9a34501f7fa',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            cookies = cookies,
            callback = self.get_about_text,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'cookies': cookies,
                'csrf_token': csrf_token,
                'item' : item
            }
        )

    def get_about_text(self, response):

        csrf_token       = response.meta['csrf_token']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json()

        about = ''

        categories_data =  [ i for i in data['included'] if ("topComponents" in i and i['topComponents']) ]
        for category_data in categories_data:
            if category_data['topComponents'][0]['components']['headerComponent']['title']['text'] == "About":
                about = category_data['topComponents'][1]['components']['textComponent']['text']['text']
                break

        item = {
            **item,
            'about': about
        }


        yield scrapy.Request(
            url = f' https://www.linkedin.com/voyager/api/graphql?variables=(profileUrn:{mini_profile_urn}d_profile{mini_profile},sectionType:experience,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.d1fbf4203e7f3e809d980fc2ff199b5f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            callback = self.get_experiences,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'csrf_token': csrf_token,
                'item' : item,
            }
        )     

    def get_experiences(self, response):

        csrf_token       = response.meta['csrf_token']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']
        data = response.json() 
        
        includes =  [ i for i in data['included'] if 'components' in i ]

        experiences = self.format_people_categories('EXPERIENCE', includes)
    
        if experiences:
            experiences = [ 
                {
                    'postion': experience['second_key'],
                    'company': experience['first_key'],
                    'company_url': experience['third_key'],
                    'time': experience['fourth_key']
                } for experience in experiences
             ]
            experiences = [ 
                experience for experience in experiences 
                if( experience['company'] and not any(char.isdigit() for char in experience['company']) )  
            ]

        item = {
            **item,
            'experiences': experiences
        }

        yield scrapy.Request(
            url = f' https://www.linkedin.com/voyager/api/graphql?variables=(profileUrn:{mini_profile_urn}d_profile{mini_profile},sectionType:education,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.d1fbf4203e7f3e809d980fc2ff199b5f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            callback = self.get_education,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'csrf_token': csrf_token,
                'item' : item,
            }
        )     
                     
    def get_education(self, response):


        csrf_token       = response.meta['csrf_token']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json() 

        includes =  [ i for i in data['included'] if 'components' in i ]

        education = self.format_people_categories("EDUCATION", includes)

        if education:
            education = [
                {
                    'major': e['first_key'],
                    'studied_at': e['second_key'],
                    'school_url': e['third_key'],
                    'time': e['fourth_key']
                } for e in education
            ]

        item = {
            **item,
            'education': education
        }

        yield scrapy.Request(
            url = f' https://www.linkedin.com/voyager/api/graphql?variables=(profileUrn:{mini_profile_urn}d_profile{mini_profile},sectionType:volunteering-experiences,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.d1fbf4203e7f3e809d980fc2ff199b5f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            callback = self.get_volunteering,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'csrf_token': csrf_token,
                'item' : item,
            }
        )     
      
    def get_volunteering(self, response):

        csrf_token       = response.meta['csrf_token']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json() 

        includes =  [ i for i in data['included'] if 'components' in i ]

        volunteering = self.format_people_categories("VOLUNTEERING", includes)

        if volunteering:
            volunteering = [
                {
                    'role'          : v['second_key'],
                    'association'   : v['first_key'],
                    'associated_url': v['third_key'],
                    'time'          : v['fourth_key']
                } for v in volunteering
            ]

        item = {
            **item,
            'volunteering': volunteering
        }
        
        yield scrapy.Request(
            url = f' https://www.linkedin.com/voyager/api/graphql?variables=(profileUrn:{mini_profile_urn}d_profile{mini_profile},sectionType:languages,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.d1fbf4203e7f3e809d980fc2ff199b5f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            callback = self.get_languages,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'csrf_token': csrf_token,
                'item' : item,
            }
        )     

    def get_languages(self, response):

        csrf_token       = response.meta['csrf_token']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json() 

        includes =  [ i for i in data['included'] if 'components' in i ]

        languages = self.format_people_categories("LANGUAGES",  includes)

        if languages:
            languages = [
                {
                    'language': language['second_key'],
                    'level': language['fourth_key']
                } for language in languages
            ]
        
        item = {
            **item,
            'languages': languages
        }

        yield scrapy.Request(
            url = f' https://www.linkedin.com/voyager/api/graphql?variables=(profileUrn:{mini_profile_urn}d_profile{mini_profile},sectionType:skills,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.d1fbf4203e7f3e809d980fc2ff199b5f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            callback = self.get_skills,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'csrf_token': csrf_token,
                'item' : item,
            }
        )     
       
    def get_skills(self, response):

        csrf_token       = response.meta['csrf_token']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json() 

        includes =  [ i for i in data['included'] if 'components' in i ]

        skills = self.format_people_categories("SKILLS", includes)

        skills = [
            {
                'skill': skill['second_key'],
                'endorsements': re.search(r'\d+', skill['fifth_key'] ).group() if skill['fifth_key'] else skill['fifth_key']
            } for skill in skills  if skills
        ]
        
        item = {
            **item,
            'skills': skills
        }

        yield scrapy.Request(
            url = f' https://www.linkedin.com/voyager/api/graphql?variables=(profileUrn:{mini_profile_urn}d_profile{mini_profile},sectionType:organizations,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.d1fbf4203e7f3e809d980fc2ff199b5f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            callback = self.get_organizations,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'csrf_token': csrf_token,
                'item' : item
            }
        )    
          
    def get_organizations(self, response):

        csrf_token       = response.meta['csrf_token']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json() 
        
        includes =  [ i for i in data['included'] if 'components' in i ]
    
        organizations = self.format_people_categories("ORGANIZATIONS", includes)

        organizations = [
            {
                'role': organization['first_key'],
                'organization': organization['second_key']
            } for organization in organizations if organizations
        ]

        item = {
            **item,
            'organizations': organizations
        }

        yield scrapy.Request(
            url = f' https://www.linkedin.com/voyager/api/graphql?variables=(profileUrn:{mini_profile_urn}d_profile{mini_profile},sectionType:honors,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.d1fbf4203e7f3e809d980fc2ff199b5f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            callback = self.get_honors,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'csrf_token': csrf_token,
                'item' : item
            }
        )    

    def get_honors(self, response):

        csrf_token       = response.meta['csrf_token']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json() 


        includes =  [ i for i in data['included'] if 'components' in i ]
    
        honors = self.format_people_categories("HONORS", includes)

        honors = [
            {
                'name': honor['second_key'],
                'issued_by': honor['first_key']
            } for honor in honors if honors
        ]

        item = {
            **item,
            'honors': honors
        }

        yield scrapy.Request(
            url = f' https://www.linkedin.com/voyager/api/graphql?variables=(profileUrn:{mini_profile_urn}d_profile{mini_profile},sectionType:certifications,locale:en_US)&&queryId=voyagerIdentityDashProfileComponents.d1fbf4203e7f3e809d980fc2ff199b5f',
            headers = {
                'accept': 'application/vnd.linkedin.normalized+json+2.1',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'csrf-token': csrf_token,
                'user-agent': utils.random_user_agent()
            },
            callback = self.get_certifications,
            errback = self.handle_error,
            meta = {
                'mini_profile_urn': mini_profile_urn,
                'mini_profile': mini_profile,
                'csrf_token': csrf_token,
                'item' : item
            }
        )    
   
    def get_certifications(self, response):

        csrf_token       = response.meta['csrf_token']
        mini_profile_urn = response.meta['mini_profile_urn']
        mini_profile     = response.meta['mini_profile']
        item             = response.meta['item']

        data = response.json() 


        includes =  [ i for i in data['included'] if 'components' in i ]
    
        certifications = self.format_people_categories("HONORS", includes)

        certifications = [
            {
                'name'       : certification['second_key'],
                'issued_by'  : certification['first_key'],
                'issued_date': certification['fourth_key'],
                'issued_url' : certification['third_key']
            } for certification in certifications if certifications
        ]

        item = {
            **item,
            'certifications': certifications
        }

        yield item