"""
Auction Module for Second-Price Sealed-Bid Online Advertising Auction.

This module implements a second-price sealed-bid auction system for online advertising,
where bidders compete to show ads to users. The auction follows standard second-price
rules where the winner pays the second-highest bid amount.

Classes:
- User: Represents a user with a fixed probability of clicking on ads
- Auction: Manages the auction mechanism between users and bidders
"""

import random
#import numpy as np
import matplotlib.pyplot as plt

class User:
    """
    Represents a user in the ad auction system.
    
    Each user has a fixed probability of clicking on any ad shown to them.
    This probability is randomly assigned during initialization and remains
    constant throughout the auction.
    
    Attributes:
        __probability (float): Hidden probability of the user clicking on an ad.
    """
    def __init__(self):
        self.click_probability = random.random()
    def show_ad(self):
        """
        Simulate showing an ad to this user.
        
        Returns:
            bool: True if the user clicked on the ad, 
                  False otherwise
                  NOTE:Probabilit of Returning True = User's click probability
        """
        return random.random() < self.click_probability


class Auction:
    """
    Manages a second-price sealed-bid auction for online advertising.
    
    This class implements the auction mechanism where bidders compete to show
    ads to users. It follows the second-price auction rules where the winner
    pays the second-highest bid amount.
    
    Attributes:
        1. users (list)       : List of User objects participating in the auction.
        2. bidders (list)     : List of Bidder objects participating in the auction.
        3. balances (dict)    : Dictionary tracking each bidder's balance.
        4. history (dict)     : Dictionary tracking auction history for visualization.
        5. round_number (int) : The current round number in the auction.
    
    """
    def __init__(self, users, bidders):
        self.users = users
        self.bidders = bidders
        # Dictionary to track each bidder's balance
        self.balances = {bidder: 0 for bidder in bidders}
        # Track auction history for visualization
        self.history = {bidder: [] for bidder in bidders}
        self.round_number = 0
    def execute_round(self):
        """
        Execute a single round of the auction.
        
        A round consists of:
        1. Selecting a random user
        2. Collecting bids from all bidders
        3. Determining the winner and price
        4. Showing an ad to the user
        5. Notifying bidders of the results
        6. Updating balances
        
        Bidders with balances below -1000 are disqualified from bidding
        """
        self.round_number += 1
        user_index = random.randrange(len(self.users))
        selected_user = self.users[user_index]
        active_bidders = [b for b in self.bidders if self.balances[b] >= -1000]
        bids = {}
        for bidder in active_bidders:
            bid_amount = bidder.bid(user_index)
            bid_amount = max(0, round(bid_amount, 3))
            bids[bidder] = bid_amount    
        if not bids:
            return
        max_bid = max(bids.values())
        max_bidders = [b for b, amount in bids.items() if amount == max_bid]
        winner = random.choice(max_bidders)
        if len(max_bidders) > 1:  
            second_price = max_bid
        else:

            second_bids = [amount for bidder, amount in bids.items()
                           if bidder != winner]
            second_price = max(second_bids) if second_bids else 0    
        clicked = selected_user.show_ad()
        for bidder in active_bidders:
            if bidder == winner:
                bidder.notify(True, second_price, clicked)
            else:
                bidder.notify(False, second_price, None)
        reward = 1 if clicked else 0
        self.balances[winner] += reward - second_price

        for bidder in self.bidders:
            self.history[winner].append(self.balances[winner])
    def plot_history(self):
        """
        Plot the history of each bidder's balance over time.
        """
        plt.figure(figsize=(10, 6))
        for bidder, history in self.history.items():

            bidder_name = type(bidder).__name__
            plt.plot(range(1, len(history) + 1), history, label=bidder_name)
        plt.xlabel('Round')
        plt.ylabel('Balance ($)')
        plt.title('Bidder Balances Over Time')
        plt.legend()
        plt.grid(True)
        plt.show()
