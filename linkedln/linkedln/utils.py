import random
from .settings import USER_AGENT_LIST
from http.cookies import SimpleCookie
from datetime import datetime

COOKIE_STRING = 'bcookie="v=2&5dc970ac-119c-4914-8bab-49b912336c35"; bscookie="v=1&202307111239015b8b993e-72d0-48b9-875c-6a5a25289c62AQGzsR9CsAxROLhsLsyNW7dJIBBJeM9I"; lang=v=2&lang=en-us; g_state={"i_l":0}; fcookie=AQGRcUNKjfBgbAAAAYlE9138bTKsoZjTthGKrN4-BB5Q7pHdhDkPYGK41RE8cIM3JWKzF-Rl8JFDwIwQhhshHDWN32poiqpc6TLHlE3ADelok1VTs6PgZYoZu6hxrKpfHIhsesdwQcMDR0w3vEToq9Ius8kX3HQjv_VgTHipY1EY-Wuq2ZbOenEdsEAOi3o7z8YE4fJl4pSNSALk-Xh7eBVXULit-zuT6yWcLLfjaWCfcJrJWMQ-8VwEvPTE-NRZcHtVhQV/QWHOn9lWICwHPvmza4nW6a8SP64JerRSYU2GobPEPkZGLCqQFmC7Aj5lxdsQC37ntoaxRPAkRQ4+qUGWamKQ==; li_at=AQEDAUFyFTUEvp8PAAABiUT3X5kAAAGJaQPjmU0Adku1pgFUUZBhqseq4QL63BlIB1-zslSdijA53ct1R4DKMcnV1fpa4Ggbq-5YzPbeXoQl5FF08g-frOYgaP1aCpudDKLCPCyothoFEIfySmHBr9AS; liap=true; JSESSIONID="ajax:4783027849707025508"; fid=AQF6Yx-Fn1_q6AAAAYlE92Ft61-_SKPhjsAfSE6Vfl4x7exgKK_3SY8k4wn-fMP-XLWn7Uxn1qDnlA; timezone=Asia/Saigon; li_theme=light; li_theme_set=app; li_sugr=bec6ccc6-a66e-434d-b02e-1207d3aee805; _guid=cd6525c1-2520-4fd1-b2be-6394b174da50; AnalyticsSyncHistory=AQKRhns3vbLrmgAAAYlE9228EV8erHvRyMuWezgcjijBuRJPQfR--xMlBOyrvYuOF1yHRrDBHXe5LIY3sff4Rw; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19550%7CMCMID%7C35067119386448832173343933525000969617%7CMCAAMLH-1689684013%7C3%7CMCAAMB-1689684013%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1689086413s%7CNONE%7CMCCIDH%7C593241078%7CvVersion%7C5.1.1; lms_ads=AQFJnnHVlMtI7wAAAYlE926-fFHsUOdHpc1Wyz2oawS0DVYvO8-FW_IQDRh1qerUVV0okTZjuKJH4bhjlBIDIFAxn0h-T-t-; lms_analytics=AQFJnnHVlMtI7wAAAYlE926-fFHsUOdHpc1Wyz2oawS0DVYvO8-FW_IQDRh1qerUVV0okTZjuKJH4bhjlBIDIFAxn0h-T-t-; aam_uuid=34873263274662473863361698451753610842; UserMatchHistory=AQIuUG-hRrk23QAAAYlFBL_6RUe1-lJLNFs018zYHQ8Ob-DNPP_B27Pz7-u5OB8cPNehC0RoFZDonjLKIVeKKEtL6j34nu1H1rug1ZzHcp7QVjI2PiaDfRrn01TX6UtakDlU8Gny9_dZPCL9v0rjM19yBFKaLUwP-amHKgUKkUOtfpMnVL8SK6bQCb-O6jQLhkwJmyVhEbssfLmxVgv88TYGC7jSvj1AOGRcMu2aaVhCGv-PSKsG2UcF5N3MxpNrB7f-cmwCZBUMixFhl67B1HhAflo3hW6MiMfEoyztaKYB-l5xZ1PyVjd3O7-p_yZjTlU7A2KNomRn-P8L96y_KlQp0JZ6uuc; lidc="b=OB73:s=O:r=O:a=O:p=O:g=2804:u=3:x=1:i=1689080087:t=1689165610:v=2:sig=AQF_x76Re5BspaAwdSPM0pMgCJ3nR7oF"'

class UtilsProcess:
   

    # Random User Agent:
    def random_user_agent(self):
        return random.choice(USER_AGENT_LIST)   
    
    def cookie_parser(self, cookie_string = COOKIE_STRING):

        cookie = SimpleCookie()
        cookie.load(cookie_string)

        cookies = {}
        for key,morsel in cookie.items():
            cookies[key] = morsel.value
        
        return cookies

utils = UtilsProcess()
