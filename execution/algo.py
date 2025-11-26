import time
import numpy as np

class ExecutionAlgo:
    def __init__(self, router):
        self.router = router

    def twap(self, symbol, side, total_quantity, duration_minutes, interval_seconds=60):
        """
        Time-Weighted Average Price (TWAP) execution.
        Slices order evenly over time.
        """
        num_slices = int((duration_minutes * 60) / interval_seconds)
        if num_slices == 0:
            return

        slice_qty = total_quantity / num_slices
        print(f"Starting TWAP: {total_quantity} {symbol} over {duration_minutes} min. Slice: {slice_qty:.4f}")

        for i in range(num_slices):
            order = {
                'symbol': symbol,
                'side': side,
                'quantity': slice_qty
            }
            self.router.route_order(order)
            # In simulation we don't actually sleep for long
            # time.sleep(interval_seconds) 
            print(f"Executed slice {i+1}/{num_slices}")

    def pov(self, symbol, side, total_quantity, participation_rate=0.10):
        """
        Percentage of Volume (POV) execution.
        Executes based on market volume to avoid impact.
        """
        remaining_qty = total_quantity
        print(f"Starting POV: {total_quantity} {symbol} at {participation_rate*100}% rate")

        while remaining_qty > 0:
            # Simulate fetching recent market volume (e.g., last minute volume)
            market_volume = np.random.uniform(10, 50) # Random placeholder
            
            # Calculate our trade size
            my_trade_size = market_volume * participation_rate
            
            if my_trade_size > remaining_qty:
                my_trade_size = remaining_qty

            order = {
                'symbol': symbol,
                'side': side,
                'quantity': my_trade_size
            }
            self.router.route_order(order)
            
            remaining_qty -= my_trade_size
            print(f"Executed {my_trade_size:.4f}. Remaining: {remaining_qty:.4f}")
            # time.sleep(60) # Wait for next volume bucket
