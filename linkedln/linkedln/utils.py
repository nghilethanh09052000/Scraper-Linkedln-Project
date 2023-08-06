import random
from .settings import USER_AGENT_LIST
from http.cookies import SimpleCookie
from datetime import datetime

COOKIE_STRING = 'lang=v=2&lang=en-us; bcookie="v=2&a9b2d6a7-7992-40b0-8dcb-9295384ad897"; bscookie="v=1&202308050748107604d22d-1b34-4789-80fa-bd5f74a306a7AQGBrmx1tP1IegfNMUFnU_GitqF23gn_"; fid=AQFhHoqPNoH2DAAAAYnErr98clUj9kMJgmJgWpjrIsSQBCK6WJmlrsukuauECChQl4qblP-XB5NaVw; fcookie=AQFrIp236cB2oAAAAYnErvgV6gy1oGiQFCL94niQu_6bfJeTgL1mZ-oN6tCDTZjBmhX7pfZ_6tTJevXMQvVuaR-J9raxTCu9DZuJI_zD6dE0eFBr3uZnhW9OMGNkK0lhl6TQfVfmUvhDFYVAtFnxeg94zGk2eikhyE5fG52X6wiWgsp1_XjJeh-X2XQ89y9SLsLpmorLUfR4EXLzr3-Sd2KWMhGtMBSkHXDmVvSU853TaHPvXspYReD1T_u8idlHVUpVXgYcn9Todm0QyHjJ+VThLlVxmZW8KAoP2BJ4mPI4omay3EK1W1qb8h/heAUTo7SdXkQIjKz2ls5vJ4TaCmDQKTnQ==; li_at=AQEDATfMlqUEYh_uAAABicSu-J8AAAGJ6Lt8n1YACNmWCxTrBg1bI1oxpuX7P_thusFzR2Kgzc5-VksopyZAfJktgZf8hil6ZU5x3OFjBsUmVQCUsbFYV43FjSVRagtGF20UD_8q9thEJQPMZTqRzouI; liap=true; JSESSIONID="ajax:5399261851523270248"; timezone=Asia/Bangkok; li_theme=light; li_theme_set=app; li_sugr=120ffa7e-e5c3-457f-93ae-00b00850be3a; _guid=c88c5bf3-e4f7-4801-a2e6-91e4f6070aff; AnalyticsSyncHistory=AQLekMb1ryP_tQAAAYnErw3H9l_c1Tj5guqMp9xIZ467OHq1TM-lxa8aL43X9i2OuLPHnwLlkXKPCSmFi0cXvg; lms_ads=AQH7VAqekTb6vgAAAYnErw8D8y39v4FYcuBNz9ayCRXAzLnO17X4VKncO3XoyEMJ98kUK12zSJfDA1wV6S5aJqQg9N-pXp7E; lms_analytics=AQH7VAqekTb6vgAAAYnErw8D8y39v4FYcuBNz9ayCRXAzLnO17X4VKncO3XoyEMJ98kUK12zSJfDA1wV6S5aJqQg9N-pXp7E; AMCVS_14215E3D5995C57C0A495C55%40AdobeOrg=1; AMCV_14215E3D5995C57C0A495C55%40AdobeOrg=-637568504%7CMCIDTS%7C19575%7CMCMID%7C60391694551805912104452853757858346374%7CMCAAMLH-1691826753%7C3%7CMCAAMB-1691826753%7C6G1ynYcLPuiQxYZrsz_pkqfLG9yMXBpb2zX5dvJdYQJzPXImdj0y%7CMCOPTOUT-1691229153s%7CNONE%7CMCCIDH%7C-1621091256%7CvVersion%7C5.1.1; aam_uuid=59808854625673061454396808298693264973; UserMatchHistory=AQJynFM6xqJUqwAAAYnE16DYFVitU684ku5P0fLGtTVev8ynn0SnDYiSvb_3cjzXzm0hx6151ddvxruYSMaf01K14x3KPAdqYTudWmq7TKsh-RZHMddONy5CT-Zn41vDZqcSTDAFipYZGAmDZGWyteKI_3VnGE9VqCfvXlJS8xJaXJtF_ZQlz33_6CurOLJDd5w4ofFND1FuIdRrb-pXoDKKXVKFLpe4V_2OpZc__qG7qKlTVHx1QTY8LvO33BQAYd-Xy64VCiivA4EjeaiIbkkCCI5SN-0WY1_stgKjYyHcAMUIG0R0NTbxucBJQPubbTxyUSHcTLf-x1TaayA_ijsB95GbDOg; lidc="b=OB89:s=O:r=O:a=O:p=O:g=3049:u=5:x=1:i=1691224614:t=1691307303:v=2:sig=AQEmTOpz9ImxOC5_1TlWOrsrocnKaYmD"'

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
