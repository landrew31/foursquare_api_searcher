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
  
  * **aggregate** - compute all data for each category
  
  * **make_weights** - calculate weight matrix using unique formula and save to file
  
  **Next with one of parameters:** *[shop_service, arts_entertainment, travel_transport, food, outdoors, all]*
  
  * **gamma_index** (*param1: str*)- calculate Gamma index for appropriate category
  
  * **join_count_statistic** (*param1: str*)- calculate Join Count statistic for appropriate category

  * **moran_one** (*param1: str*)- calculate Moran`s I index for appropriate category
  
  * **geary_c** (*param1: str*)- calculate Geary's C index for appropriate category
  
  * **local_moran** (*param1: str*)- calculate Local Moran`s I index for appropriate category
  
  * **sem** (*param1: str*)- run Spatial Error Model for count of vanues for appropriate category
  
  * **sar** (*param1: str*)- run Spatial Autoregressive Model (Spatial Lag Model) for count of vanues for appropriate category
  
  * **durbin** (*param1: str*)- run Spatial Durbin Model for count of vanues for appropriate category
  
