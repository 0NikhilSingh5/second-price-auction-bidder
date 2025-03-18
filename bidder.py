"""
Second-Price Ad Auction Bidding Agent

This module implements an bidding agent for second-price ad auctions.

The bidding strategy combines Thompson sampling with Upper Confidence Bound
techniques to effectively balance exploration and exploitation throughout the auction
lifecycle. The agent adaptively learns user click probabilities and competitor bidding
patterns to maximize ROI.

Classes:
    Bidder: Core bidding agent with methods for bid generation and processint the results.

Dependencies:
    - numpy (>=1.18.0): For numerical operations and statistical sampling
"""

import numpy as np

class Bidder:
    """
    A bidding agent for a second-price ad auction.
    
    Attributes:
        1. num_users (int)       : Total users in the auction.
        2. num_rounds (int)      : Total auction rounds.
        3. user_data (dict)     : Dictionary containing user performance metrics.
        4. auction_config (dict): Dictionary containing auction parameters.
        5. current_round (int)   : Current round number.
        6. last_user_id (int)    : ID of the most recent user targeted.
        7. last_bid (float)      : Most recent bid amount.
    """

    def __init__(self, num_users, num_rounds):
        """
        Initialize the bidder with parameters for the auction.
        
        Args:
            num_users (int) : Total number of users in the auction.
            num_rounds (int): Total number of rounds in the auction.
        """
        self.num_users = num_users
        self.num_rounds = num_rounds
        #consolidated user performance data
        self.user_data = {
            'clicks': np.zeros(num_users),
            'impressions': np.zeros(num_users),
            'click_probs': np.full(shape=num_users, fill_value=0.45),
            'winning_prices': [[] for _ in range(num_users)]
        }
        #Auction configuration parameters
        self.auction_config = {
            'exploration_factor': 2.0,  # Higher values favor exploration
           'min_bid': 0.01,             # Minimum bid to ensure we participate
           'max_bid': 0.95              # Maximum bid to avoid overpaying
        }
        #Tracking State
        self.current_round = 0
        self.last_user_id = None
        self.last_bid = None
    def bid(self, user_id):
        """
        Generate a bid for the given user based on historic performance.
        
        Uses Thompson sampling with Beta distribution and UCB-inspired exploration
        bonus to determine bid amount.
        
        Args:
            user_id (int): The ID of the user to bid on.
        Returns:
            float: The bid amount, rounded to 3 decimal places.
        """
        # Update tracking variables
        self.current_round += 1
        self.last_user_id = user_id
        # Extract user data for easier access
        clicks = self.user_data['clicks'][user_id]
        impressions = self.user_data['impressions'][user_id]
        winning_prices = self.user_data['winning_prices'][user_id]
        # Calculate exploration parameters
        progress = self.current_round / self.num_rounds
        exploration_decay = 1.0 / (1 + self.current_round / self.num_rounds)
        # Calculate estimated click probability with exploration bonus
        if impressions == 0:
            # For users we haven't seen yet, use a high exploration bid
            estimated_value = 0.5  # Use a neutral prior
            # Exploration bonus decreases as auction progresses
            exploration_bonus = self.auction_config['exploration_factor'] * exploration_decay
        else:
            # For users we've seen, use observed click rate
            estimated_value = clicks / impressions
            # Add exploration bonus (UCB approach)
            log_term = np.log(self.current_round + 1)
            impression_term = impressions + 1
            exploration_bonus = (self.auction_config['exploration_factor']*
                                 np.sqrt(log_term / impression_term))
        # Calculate Thompson sampling parameters
        alpha = clicks + 1  # Add 1 as prior (1 success)
        beta = impressions - clicks + 1  # Add 1 as prior (1 failure)
        # Sample from beta distribution to estimate true click probability
        sampled_value = np.random.beta(alpha, beta)
        # Combine estimated value with exploration bonus
        value_estimate = sampled_value + exploration_bonus * (1 - sampled_value)
        # Calculate average winning price for this user (if we have data)
        if winning_prices:
            avg_price = np.mean(winning_prices)
            # Adjust our bid based on average price and our value estimate
            if value_estimate > avg_price:
                # If user is valuable, bid slightly above average price
                bid_amount = min(value_estimate, avg_price * 1.1)
            else:
                # If user is less valuable, bid conservatively
                bid_amount = value_estimate * 0.9
        else:
            # If we don't have price data, use our value estimate directly
            bid_amount = value_estimate
        # Apply strategic adjustments based on game progress
        if progress < 0.2:
            # Early game: Prioritize exploration
            bid_amount = max(bid_amount, self.auction_config['min_bid'] * 3)
        elif progress > 0.8:
            # Late game: Focus on high-value users
            if estimated_value > 0.7:
                bid_amount = max(bid_amount, value_estimate * 0.95)
            else:
                bid_amount = min(bid_amount, value_estimate * 0.8)
        # Limiting bid
        min_bid = self.auction_config['min_bid']
        max_bid = self.auction_config['max_bid']
        bid_amount = max(min_bid, min(max_bid, bid_amount))
        self.last_bid = round(bid_amount, 3)
        return self.last_bid
    def notify(self, auction_winner, winning_price, clicked):
        """
        Process notifications about auction results.
        
        Updates bidder's internal models based on auction outcomes to improve
        future bidding decisions.
        
        Args:
            auction_winner (bool) : True if this bidder won the auction.
            winning_price (float) : The second-highest bid (price paid).
            clicked (bool or None): Whether the user clicked (None if lost).
        """
        # Update our records if we have data from the previous bid
        if self.last_user_id is None:
            return
        # Record the winning price for the user
        user_id = self.last_user_id
        self.user_data['winning_prices'][user_id].append(winning_price)
        # Keep only the 10 most recent prices to adapt to changing conditions
        if len(self.user_data['winning_prices'][user_id]) > 10:
            self.user_data['winning_prices'][user_id].pop(0)
        if auction_winner:
            # Update our records if we won
            self.user_data['impressions'][user_id] += 1
            if clicked:
                self.user_data['clicks'][user_id] += 1
            # Update estimated click probability
            impressions = self.user_data['impressions'][user_id]
            if impressions > 0:
                clicks = self.user_data['clicks'][user_id]
                self.user_data['click_probs'][user_id] = clicks / impressions
