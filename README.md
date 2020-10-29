# dna-search

## Configuration
* Install required packages `pip install -r requirements.txt` 
* Set `DATABASE_URL` environment variable accordingly
* Run database migrations via `python manage.py migrate`
* Create a user via `python manage.py createsuperuser`
    * Here our user  is `admin:ginkgobioworks`
* 

## Stuff to build


- Pages
  - Login page
  - Dna search page to enable new searches and display results
  - Logout page/link
- Task queue using rq for dna searches
- Database model of DNA search results
- Database (maybe) of DNA strings to search
  - Maybe just hardcode for now, see how time goes