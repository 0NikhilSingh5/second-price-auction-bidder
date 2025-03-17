import numpy as np

class Bidder:
    def __init__(self, num_users, num_rounds):
        self.num_users = num_users
        self.num_rounds = num_rounds
        #consolidated user performance data
        self._user_data = {
            'clicks': np.zeros(num_users),
            'impressions': np.zeros(num_users),
            'click_probs': np.full(shape=num_users, fill_value=0.45),
            'winning_prices': [[] for _ in range(num_users)]
        }
        #Auction configuration parameters
        self._auction_config = {
            'exploration_factor': 2.0,  # Higher values favor exploration
           'min_bid': 0.01,             # Minimum bid to ensure we participate
           'max_bid': 0.95              # Maximum bid to avoid overpaying
        }
        #Tracking State
        self.current_round = 0
        self.last_user_id = None
        self.last_bid = None
    def bid(self, user_id):
        # Update tracking variables
        self.current_round += 1
        self.last_user_id = user_id
        # Extract user data for easier access
        clicks = self._user_data['clicks'][user_id]
        impressions = self._user_data['impressions'][user_id]
        winning_prices = self._user_data['winning_prices'][user_id]
        # Calculate exploration parameters
        progress = self.current_round / self.num_rounds
        exploration_decay = 1.0 / (1 + self.current_round / self.num_rounds)
        # Calculate estimated click probability with exploration bonus
        if impressions == 0:
            # For users we haven't seen yet, use a high exploration bid
            estimated_value = 0.5  # Use a neutral prior
            # Exploration bonus decreases as auction progresses
            exploration_bonus = self._auction_config['exploration_factor'] * exploration_decay
        else:
            # For users we've seen, use observed click rate
            estimated_value = clicks / impressions
            # Add exploration bonus (UCB approach)
            log_term = np.log(self.current_round + 1)
            impression_term = impressions + 1
            exploration_bonus = (self._auction_config['exploration_factor']*
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
            bid_amount = max(bid_amount, self._auction_config['min_bid'] * 3)
        elif progress > 0.8:
            # Late game: Focus on high-value users
            if estimated_value > 0.7:
                bid_amount = max(bid_amount, value_estimate * 0.95)
            else:
                bid_amount = min(bid_amount, value_estimate * 0.8)
        # Limiting bid
        min_bid = self._auction_config['min_bid']
        max_bid = self._auction_config['max_bid']
        bid_amount = max(min_bid, min(max_bid, bid_amount))
        self.last_bid = round(bid_amount, 3)
        return self.last_bid
    def notify(self, auction_winner, winning_price, clicked):
        # Update our records if we have data from the previous bid
        if self.last_user_id is None:
            return
        # Record the winning price for the user
        user_id = self.last_user_id
        self._user_data['winning_prices'][user_id].append(winning_price)
        # Keep only the 10 most recent prices to adapt to changing conditions
        if len(self._user_data['winning_prices'][user_id]) > 10:
            self._user_data['winning_prices'][user_id].pop(0)
        if auction_winner:
            # Update our records if we won
            self._user_data['impressions'][user_id] += 1
            if clicked:
                self._user_data['clicks'][user_id] += 1
            # Update estimated click probability
            impressions = self._user_data['impressions'][user_id]
            if impressions > 0:
                clicks = self._user_data['clicks'][user_id]
                self._user_data['click_probs'][user_id] = clicks / impressions
