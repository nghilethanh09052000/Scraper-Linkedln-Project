@echo off
setlocal enabledelayedexpansion

REM Define the list of alphabet letters
set "letters=abcdefghijklmnopqrstuvwxyz"

REM Loop through each letter and call scrapy crawl with the -a keyword argument
for /L %%i in (0, 1, 25) do (

    set "keyword=!letters:~%%i,1!"
    if not "!keyword!" == "" (
        echo scrapy crawl profile -a keyword=!keyword! -o profile_!keyword!.json
    )

)