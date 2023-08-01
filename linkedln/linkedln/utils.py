import random
from .settings import USER_AGENT_LIST
from http.cookies import SimpleCookie
from datetime import datetime

COOKIE_STRING = 'lang=v=2&lang=en-us; bcookie="v=2&33a3cc23-556c-4695-897c-88289fe6ee64"; bscookie="v=1&20230801113816cb517308-36fb-43ea-857e-0a7bde9e1732AQFKyWcDPUO0MsGdBP7nI-fvht0i4H5z"; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; aam_uuid=11999333309046620160653044645463905076; _gcl_au=1.1.481340351.1690890242; li_at=AQEDATfMlqUB5tuwAAABibEeexsAAAGJ1Sr_G1YAtuvNh5d9yVvI0Xs0Lhbaj3fdoqZTEiRhN37KeCKdhpu_64PiB9_2FaE-UvHCW-Ix3gEMSPQPCnOCAbCgNmZMo7PVTMdPxNVynz-hJLkr94Q5E_0Y; liap=true; JSESSIONID="ajax:0175480595477298187"; timezone=Asia/Saigon; li_theme=light; li_theme_set=app; li_sugr=a15dd221-3caa-489b-85d1-e056008fe5f8; _guid=9ca157f8-da93-497e-9ed6-82d7af8886a4; UserMatchHistory=AQLqkBWlVisbqQAAAYmxH6c1HcJdH6ArG4ytP1tPO-rr37kxOdFUPvxTZsWmGWOwbKF5577M1A-RzcMeewWTCIMDlPflRgpb1JUllGEeaCaguyvq5j6kWnZyKfSgULtBqzfHIKxx4NcsL-DkyZO_yfBLK50fyvheMtF1NkfiI1eM-ywnqiKfJeI92pJCjQmkjpx38MPMbh4xLh1EldfV7Wn4xLJ5izgcrxLd8yqGBfC9ksRNc6QpSBjMFhBHCZsOTRVsPOuTBe3VGuFjEFo4aD_lSFgnzdxGUH78s3JJIHxjwD_mgQT3IZ2s3PCXCcf0JWay70keKz9Wb84blN7KrEa1L0EGELQ; AnalyticsSyncHistory=AQKYbY4NTohMAQAAAYmxH6c15dLRDLbcdFALs6wwtytIJTxgEJZSKLUtsBSouWYtVu-4Bw6KUS0O31DlABPknQ; lms_ads=AQGpwdRRpiJa5QAAAYmxH7TV2X3Zx5_Q6zYmIzfSpEJRWEuSxu5oXr_6fWq0u0MNpT-YOFznhgg_G-HKEKb6M2WltFnQFyiX; lms_analytics=AQGpwdRRpiJa5QAAAYmxH7TV2X3Zx5_Q6zYmIzfSpEJRWEuSxu5oXr_6fWq0u0MNpT-YOFznhgg_G-HKEKb6M2WltFnQFyiX; lidc="b=OB89:s=O:r=O:a=O:p=O:g=3045:u=5:x=1:i=1690893806:t=1690958517:v=2:sig=AQFxMU9AI74sLssVThEFNQ1MYq3xKPQ6"; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19571%7CMCMID%7C11822413457179084270711352797142589695%7CMCAAMLH-1691498610%7C3%7CMCAAMB-1691498610%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1690901010s%7CNONE%7CvVersion%7C5.1.1%7CMCCIDH%7C-1621091256'

class UtilsProcess:
   

    # Random User Agent:
    def random_user_agent(self):
        return random.choice(USER_AGENT_LIST)   
    
    def cookie_parser(self, cookie_string = COOKIE_STRING):

        cookie = SimpleCookie()
        cookie.load(cookie_string)

        cookies = {}
        for key, morsel in cookie.items():
            cookies[key] = morsel.value
        return cookies

utils = UtilsProcess()
