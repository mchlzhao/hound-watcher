# HoundWatcher

Python application using Selenium WebDriver that scrapes betting site odds of horse and greyhound races in real time, and calculates the most profitable bets under various bookie promotions.

## TODO:
- Implement BlueBet scraper
- Fix the way `main.py` manages threads: need to start/stop scrapers on-demand, maybe spawn child processes instead?
- Create proper `DataStore` class
- Turn promotion EV functions into classes
- Find clean way to fetch/push odds/EV information for display
- Create a proper GUI