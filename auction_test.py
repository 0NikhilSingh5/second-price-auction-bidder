import unittest
from unittest.mock import patch, MagicMock
from auction import User, Auction
from bidder import Bidder

class TestAuctionSystem(unittest.TestCase):

    def setUp(self):
        # Create a fixed set of users and bidders for testing
        self.num_users = 3
        self.num_rounds = 10
        self.users = [User() for _ in range(self.num_users)]
        self.bidders = [Bidder(self.num_users, self.num_rounds) for _ in range(2)]
        self.auction = Auction(self.users, self.bidders)

    def test_user_click_behavior(self):
        """Test if User click behavior is consistent with its probability"""
        user = User()
        
        # Control the random value to ensure consistent behavior
        with patch('random.random', side_effect=[0.3, 0.2, 0.8, 0.4]):
            # Set internal click probability to 0.5 for testing
            user._User__click_probability = 0.5
            
            # User should click when random value (0.3) < click probability (0.5)
            self.assertTrue(user.show_ad())
            
            # User should click when random value (0.2) < click probability (0.5)
            self.assertTrue(user.show_ad())
            
            # User should not click when random value (0.8) > click probability (0.5)
            self.assertFalse(user.show_ad())
            
            # User should click when random value (0.4) < click probability (0.5)
            self.assertTrue(user.show_ad())

    def test_bidder_bid_functionality(self):
        """Test if Bidder's bid function returns values within expected range"""
        bidder = Bidder(self.num_users, self.num_rounds)
        
        # Test bid for a user
        bid = bidder.bid(user_id=0)
        
        # Bid should be within the min and max bid range
        self.assertGreaterEqual(bid, bidder._auction_config['min_bid'])
        self.assertLessEqual(bid, bidder._auction_config['max_bid'])
        
        # Test bid precision (should be rounded to 3 decimal places)
        self.assertEqual(round(bid, 3), bid)

    def test_auction_execute_round(self):
        """Test if auction round executes correctly"""
        # Mock the bidders and users to control their behavior
        mock_user = MagicMock()
        mock_user.show_ad.return_value = True  # User always clicks
        
        mock_bidder1 = MagicMock()
        mock_bidder1.bid.return_value = 0.5
        
        mock_bidder2 = MagicMock()
        mock_bidder2.bid.return_value = 0.3
        
        # Create auction with mocked components
        auction = Auction([mock_user], [mock_bidder1, mock_bidder2])
        
        # Control random selection to ensure consistent behavior
        with patch('random.randrange', return_value=0), \
             patch('random.choice', return_value=mock_bidder1):
            
            # Execute a round
            auction.execute_round()
            
            # Check if the auction called the right methods
            mock_user.show_ad.assert_called_once()
            mock_bidder1.bid.assert_called_once()
            mock_bidder2.bid.assert_called_once()
            
            # Check if the bidders were notified correctly
            mock_bidder1.notify.assert_called_once_with(True, 0.3, True)  # Winner, second price, clicked
            mock_bidder2.notify.assert_called_once_with(False, 0.3, None)  # Loser, second price, None
            
            # Check if the balance was updated correctly (reward - second price)
            self.assertEqual(auction.balances[mock_bidder1], 1 - 0.3)

    def test_bidder_learning(self):
        """Test if bidder updates its model based on auction results"""
        bidder = Bidder(self.num_users, self.num_rounds)
        
        # Simulate a won auction for user 0 with a click
        bidder.last_user_id = 0
        bidder.notify(True, 0.4, True)
        
        # Check if the bidder updated its records
        self.assertEqual(bidder._user_data['impressions'][0], 1)
        self.assertEqual(bidder._user_data['clicks'][0], 1)
        self.assertEqual(bidder._user_data['click_probs'][0], 1.0)
        self.assertEqual(bidder._user_data['winning_prices'][0], [0.4])
        
        # Simulate another won auction for user 0 without a click
        bidder.notify(True, 0.3, False)
        
        # Check if the bidder updated its records correctly
        self.assertEqual(bidder._user_data['impressions'][0], 2)
        self.assertEqual(bidder._user_data['clicks'][0], 1)
        self.assertEqual(bidder._user_data['click_probs'][0], 0.5)
        self.assertEqual(bidder._user_data['winning_prices'][0], [0.4, 0.3])

if __name__ == '__main__':
    unittest.main()