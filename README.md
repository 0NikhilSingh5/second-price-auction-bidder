# Second-Price Ad Auction - ML-Based Bidding System

This project implements a Second-Price Sealed-Bid Auction system for online advertising. The auction system consists of Users, Bidders, and an Auction manager that executes multiple rounds of bidding.

The goal is to design a smart bidding agent that strategically balances exploration and exploitation to maximize profits while competing against other bidders

## ❓ How the auction works:
* Each **User** has a **secret probability** of clicking an ad.

* Each **Bidder** submits a bid to display an ad when a user visits a page.

* The highest bidder wins, but they only pay the second-highest bid amount.

* The winner gains $1 if the user clicks on the ad, but loses the bid amount.

* The auction continues for a predefined number of rounds.

## 📂Project files
auction.py - Implements the User and Auction classes.

bidder.py - Implements the Bidder class with an intelligent bidding strategy.

## ⭐Installation & Setup
### Clone the Repository
```bash
git clone https://github.com/0NikhilSingh5/second-price-auction-bidder.git
cd second-price-auction-bidder
```
### Install Dependencies
```bash
pip install numpy 
```

## ⚒️Code Breakdown

**1. User class**

Each User has a fixed probability of clicking an ad, which is randomly assigned.
```python
import random
class User:
    def __init__(self):
        """Initialize user with a random click probability."""
        self.__probability = random.random()

    def show_ad(self):
        """Simulates showing an ad. Returns True if clicked."""
        return random.random() < self.__probability
```

**2. Bidder Class (Intelligent Bidding Agent)**

The Bidder class implements an adaptive learning strategy combining:

* Thompson Sampling (Bayesian inference for click probability estimation).

* Upper Confidence Bound (UCB) (To balance exploration vs exploitation).
```python
import numpy as np

class Bidder:
    def __init__(self, num_users, num_rounds):
        """Initialize the bidder with auction parameters."""
        self.num_users = num_users
        self.num_rounds = num_rounds
        self.user_data = {
            'clicks': np.zeros(num_users),
            'impressions': np.zeros(num_users),
            'click_probs': np.full(num_users, 0.45),
            'winning_prices': [[] for _ in range(num_users)]
        }

    def bid(self, user_id):
        """Generate an optimal bid based on historical performance."""
        clicks = self.user_data['clicks'][user_id]
        impressions = self.user_data['impressions'][user_id]
        
        if impressions == 0:
            estimated_value = 0.5  # Default estimate for unseen users
        else:
            estimated_value = clicks / impressions
        
        bid_amount = estimated_value * 0.9  # Conservative bidding strategy
        return round(bid_amount, 3)

    def notify(self, auction_winner, winning_price, clicked):
        """Update internal models based on auction results."""
        if auction_winner:
            self.user_data['impressions'][self.last_user_id] += 1
            if clicked:
                self.user_data['clicks'][self.last_user_id] += 1
```

**3. Auction Class** 

The Auction class manages the bidding process, determines the winner, and updates balances.
```python
class Auction:
    def __init__(self, users, bidders):
        """Initialize auction with users and bidders."""
        self.users = users
        self.bidders = bidders
        self.balances = {bidder: 0 for bidder in bidders}

    def execute_round(self):
        """Conducts a single auction round."""
        user = random.choice(self.users)
        bids = {bidder: bidder.bid(user) for bidder in self.bidders}
        winner = max(bids, key=bids.get)
        second_price = sorted(bids.values())[-2] if len(bids) > 1 else 0
        clicked = user.show_ad()
        self.balances[winner] += (1 if clicked else 0) - second_price
```

## ⚙️How to run the auction:
### Example Simulation
```python
    if __name__ == "__main__":
    users = [User() for _ in range(10)]
    bidders = [Bidder(num_users=10, num_rounds=100) for _ in range(5)]
    auction = Auction(users, bidders)
    
    for _ in range(100):
        auction.execute_round()
```
## 📈📊 Results & Performance 

* The Bidder adapts over time, learning which users have higher click probabilities.

* The Auction follows a second-price sealed-bid mechanism.

* The strategy ensures a balance between exploration (testing new users) and exploitation (bidding more on valuable users).


## License

This project is open-source and licensed under the MIT License.



## Code Quality score

[[![Pylint Score](https://img.shields.io/badge/pylint-9.29-yellow)](PYLINT_SCORE.md)](PYLINT_SCORE.md)]
<sub>This score is given by pylint and it updates automatically when changes are pushed to this repository</sub>
