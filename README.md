# dna-search

## Example

This application in running in production at [https://dna-searcher.herokuapp.com](https://dna-searcher.herokuapp.com) with a few users with the following `username:password` pairs:
* A user I've used for testing in `admin:ginkgobioworks`
* Another user also used for testing `scientist:ginkgobioworks` 
* And a third unused user `another-scientist:ginkgobioworks`

## Setup
* Install [Python 3](https://www.python.org/downloads/), [Heroku](https://devcenter.heroku.com/articles/heroku-cli), and [PostgreSQL](https://www.postgresql.org/download/)
* Clone this repository
* Create a virtualenv for the project:
  * `python3 -m venv virtual-environment`
* Activate the virtualenv:
  * `source virtual-environment/bin/activate` (or the corresponding script for your shell of choice)
* Install required packages inside the virtualenv
  * `pip install -r requirements.txt` 
* Create a new application inside Heroku. In this case I named mine `dna-searcher`
* Provision Postgres from Heroku for your application like:
  * `heroku addons:create heroku-postgresql:hobby-dev -a dna-searcher`
* Provision Redis from Heroku for your application like:
  * `heroku addons:create heroku-redis:hobby-dev -a dna-searcher`
* Create a `.env` file in the same folder as `Procfile` containing your Postgres and Redis connection URLs output from the above commands like:
```
DATABASE_URL=postgres://username:password@hostname.compute-1.amazonaws.com:port/databasename
REDIS_URL=redis://user:password@hostname.compute-1.amazonaws.com:port
```
* Run database migrations via `python manage.py migrate` from the `dnasearch` directory
* Create a user via `python manage.py createsuperuser` from the `dnasearch` directory
* Run the application via `heroku local`
    
## Deployment

Complete the steps above and finally:
* Setup a git remote for the repository in Heroku:
  * `heroku git:remote -a dna-searcher`
* Deploy the application to Heroku via:
  * `git push heroku main`
* Start the RQ worker via `heroku scale worker=1`

## Functionality/design

This application uses Django, Redis, RQ (Redis Queue), and Postgres to implement the requirements for the DNA searching application. 

On the frontend we use vanilla JavaScript to implement basic functionality of creating DNA search requests, listing requests for a user, and automatically reloading the requests for the current user every 5 seconds. 

On the backend, we define a login view and a single view (`home.html`) for our logged-in state inside our application. These serve up the basic pages we require to the frontend. We also define two endpoints. The first is a GET endpoint `/user-searches/` to fetch all searches for the logged in user.

User searches are modeled using the `DnaSearch` model. This model contains the basic information about a search: 
* the state of the search 
* the time it was started/completed
* the user performing a search
* the string being searched for
* the resulting protein + offsets (if found)

The second is a POST endpoint `/start-search/` to create new DNA search requests, which simply accepts an object consisting of a DNA string to search for. This object is translated into a `DnaSearch` for the current user, written to Postgres, and enqueued to an RQ queue for async processing.

Our RQ worker (defined in `dna_search_task.py`) picks up this task, computes a random order of proteins to search, loads protein data protein-by-protein, and searches each protein sequence until either a match is found or there are no proteins left to search. At that point the database is updated with a result which the frontend will shortly fetch.

Protein data is stored as flat genbank files which are loaded by the worker above one-by-one. The file format was arbitrarily chosen, but the flat storage was chosen for simplicity and also time constraints. This would extend fine to a fairly large set of protein data, and you could imagine trivially using something like S3/EBS instead of the packaged list of files here, but at some point we'd probably want to move to a better search strategy via some sort of indexed memory-based datastore. I also listed some other storage improvement ideas below that could make the system more efficient in practice, but which weren't implemented here due to time constraints.

Users and login are managed via Django's built-in user and authentication mechanisms.
  
## Things that could be improved upon
In general to complete this project in a reasonable amount of time, a number of corners were cut that wouldn't be in a true production application. Below lists some of the issues and improvements that would be made in practice:
* Error handling/messaging is not really done at all. There is enough validation of the requests made that users can't get into invalid states, but things like network errors are not handled throughout. This means that tasks can be lost if they fail and also don't checkpoint their search progress. We can also end up with a bad record in the database if enqueuing to the task queue after our DB write fails. To improve this I would add more exception handling, as well as spend more time on task queue persistence + retry handling/scheduling to ensure tasks ultimately are completed. We could also use a transaction to avoid the enqueue failure issue, rolling back the DB write if the enqueue doesn't succeed. 
* Frontend styling/user feedback/presentation is not ideal. Auto-refresh is implemented, but there isn't an indication to a user that this is happening and failures/error messaging isn't handled if a request failed. To improve this I would add more UI affordances, improve/expand our displayed information and results, and add actual error handling on the frontend.
* Django is deployed in development mode and our application `SECRET_KEY` is committed into the repo. This would be woefully insecure for a production application, but would be fixable by setting that value as an environment variable in Heroku and loading the value from there.
* There's no way to register users beyond adding them manually via the Django console. To fix this I would implement a registration page/flow.
* In general all of the frontend JavaScript logic/state-management is written in a less-than-ideal way. There are likely better patterns that could be used like components, event flows, and immutable data using a more modern frontend framework like React. To fix this I would likely rewrite the frontend in terms of components + an event flow which uses immutable data.
* The time zone of the app is UTC and the Python `datetime`s aren't setting a timezone. This could be updated to a more meaningful timezone for users and to more-correctly handle these timezones on the backend.
* DNA sequences are loaded from a flat set of files that are bundled alongside the application and read from disk each time a search is performed. At scale we'd want to make numerous improvements here. Some ideas: 
    * use more of real database to store these sequences
    * make it easier to include new sequences without code changes
    * likely introduce some memory-based caching to avoid slower/repeated disk reads for each sequence
    * figure out a more ideal way to index DNA beyond effectively randomly searching a set of Strings. 
* Generally things aren't split out logically to the standard I'd expect in a production application. For example all our endpoints live in `views.py`, all our models in `models.py` etc. which will become messy if the application grows. To fix this we could refactor our code structure to introduce more classes/modules with better defined responsibilities.
* We don't really have tests for our application logic, and our code arguably isn't written in a very testable fashion. We don't have much business logic today to test, but we'd want to develop some better tests once the scope of our application grew.
* No CI/CD/monitoring/metrics/logging/alerting exist beyond anything you get for free with Heroku. To fix this we could implement various tools/frameworks to handle all of the above.
