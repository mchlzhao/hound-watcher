# HoundWatcher

Python application using Selenium WebDriver that scrapes betting site odds of horse and greyhound races in real time, and calculates the most profitable bets under various bookie promotions.

## TODO:
- Text boxes for configurable params, e.g.
  - Bet size
  - Max acceptable odds
- Create proper `DataStore` class
- Turn promotion EV functions into classes
- Find clean way to fetch/push odds/EV information for display
- Fit and incorporate statistical model to predict $\mathbb{P}(\text{3rd place})$ as a function of $\mathbb{P}(\text{2nd place})$ in cases where the Betfair place market's placing doesn't line up with the promotion
- Betfair automatically scrape all win and place markets