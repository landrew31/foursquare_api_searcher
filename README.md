# foursquare_api_searcher

## 1. Installation

  > sudo apt-get install python3-pip
  >
  > sudo pip3 install virtualenv
  >
  > sudo virtualenv -p usr/bin/python3 ENV_NAME
  >
  > cd ENV_NAME
  >
  > source bin/activate
  >
  > mkdir src
  >
  > cd src
  >
  > git clone https://github.com/landrew31/foursquare_api_searcher.git
  >
  > cd foursquare_api_searcher
  >
  > pip3 install -r requirements.txt
  
  To use project second time after installation run only:
  
  > cd ENV_NAME
  >
  > source bin/activate
  >
  > cd src/foursquare_api_searcher
  
  
## 2. Usage

  After installation o
  Run in console with command:
  
  > python3 run.py COMMAND param1 param2 ...
  
  
## 3. Possible commands

  * **run_from_number** (*param1: int*) - run searching with foursquare API starting with map square number param1
  
  * **parse_square** (*param1: int*) - search vanues exactly for square number param1
  
  * **get_categories** - get .csv file with list of main categories with its subcategories
  
  * **regionalize** (*param1: int, param2: int*) - compose all the subsquares into squares, dividing map on param1
  slices by vertical, and param2 slices by horizontal (recommended - 8 7)
