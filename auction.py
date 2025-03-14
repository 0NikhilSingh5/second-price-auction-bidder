import random
import numpy as np
import matplotlib.pyplot as plt  # Uncomment for local testing

class User:
    def __init__(self):
        self.__click_probability = random.random()
    def show_ad(self):
        return random.random() < self.__click_probability


class Auction:
    def __init__(self, users, bidders):
        self.users = users
        self.bidders = bidders
        # Dictionary to track each bidder's balance
        self.balances = {bidder: 0 for bidder in bidders}
        # Track auction history for visualization
        self.history = {bidder: [] for bidder in bidders}
        self.round_number = 0
    
    def execute_round(self):
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
            if bidder in active_bidders:
                if bidder == winner:
                    balance_change = reward - second_price
                else:
                    balance_change = 0
            else:
                balance_change = 0
            
            self.history[bidder].append(self.balances[bidder])
    
    def plot_history(self):

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
        
        pass