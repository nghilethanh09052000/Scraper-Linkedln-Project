import random
from .settings import USER_AGENT_LIST
from http.cookies import SimpleCookie
from datetime import datetime

COOKIE_STRING = 'bcookie="v=2&ed64b5e0-4708-47f7-893d-4ec2c59d33c5"; bscookie="v=1&202308010607112cb78cd3-5016-443f-8e6e-18e7a40fbc5fAQG2V8Xi0wCQXn7wSMeSNjPc1oJGkUgy"'

class UtilsProcess:
   

    # Random User Agent:
    def random_user_agent(self):
        return random.choice(USER_AGENT_LIST)   
    
    def cookie_parser(self, cookie_string):

        cookie = SimpleCookie()
        cookie.load(cookie_string)

        cookies = {}
        for key,morsel in cookie.items():
            cookies[key] = morsel.value
        
        return cookies

utils = UtilsProcess()
