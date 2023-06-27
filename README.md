# homecore

These are some core utilities I wrote for myself because I lean on them repeatedly here at home.

- `__auth__` database secrets file
- `__env__` env file for setting absolute disk pathing independent of apps
- `__version__` a version module
- `api` an API wrapper via Flask
- `app` a Flask app with a login route and a uniform wrapper/behavior for all buttons
- `auditor` my callable context manager for auditing data pipelines from request to batch to line-processor.
- `chartmaker` a wrapper to output basic chart objects (pie, donut, line, dot, bar, barh) using a basic dialect
- `coupler` intentional coupling of data model, data processor, payload validator, support methods, and endpoint(name) to register in a flask API
- `database` secure connection management and a request object wrapping the `psycopg2` module for PostgreSQL
- `logger` my logging idiom
- `model` some SQLAlchemy object models corresponding to the `auditor`
- `rcv` an algorithm I wrote to reflect how many possible ballots are possible under ranked-choice voting
- `screenshot_url` this uses Selenium and Chrome webdriver to make a screenshot of a URL
- `send_mail` an integration with the SendGrid API so I can send authenticated emails programatically
