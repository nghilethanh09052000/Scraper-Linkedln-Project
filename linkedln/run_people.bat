@echo off
setlocal enabledelayedexpansion

REM Define the list of alphabet letters
set "letters=bcdefghijklmnopqrstuvwxyz"

REM Loop through each letter and call scrapy crawl with the -a keyword argument
for /L %%i in (0, 1, 25) do (

    set "keyword=!letters:~%%i,1!"
    if not "!keyword!" == "" (
        echo scrapy crawl people_url -a keyword=!keyword! -o people_url_!keyword!.json
    )

)