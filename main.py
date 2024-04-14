import pandas as pd
import numpy as np
import os

class TradingProgram:
    def __init__(self):
        self.bankroll = 4000
        self.csv_file_path = 'trades.csv'
        if os.path.exists(self.csv_file_path):
            self.trades = pd.read_csv(self.csv_file_path, parse_dates=['time'])
        else:
            # Include all expected columns right from the start
            self.trades = pd.DataFrame(columns=["time", "price_t1", "quantity", "price_t2", "profit", "kelly_fraction", "sharpe_ratio"])
        self.kelly_fraction = 0.1

    def record_trade(self, price_t1, quantity, price_t2):
        value_per_tick = 1.25
        time = pd.Timestamp.now()
        profit = ((price_t2 * quantity) - (price_t1 * quantity)) * value_per_tick

        # Ensuring all columns are present
        new_trade = pd.DataFrame({
            "time": [time], 
            "price_t1": [price_t1], 
            "quantity": [quantity],
            "price_t2": [price_t2], 
            "profit": [profit],
            "kelly_fraction": [np.nan],  # Initialize as NaN
            "sharpe_ratio": [np.nan]    # Initialize as NaN
        })
        self.trades = pd.concat([self.trades, new_trade], ignore_index=True)
        self.update_kelly_fraction()
        self.save_trades()

    def save_trades(self):
        try:
            self.trades.to_csv(self.csv_file_path, columns=["time", "price_t1", "quantity", "price_t2", "profit", "kelly_fraction", "sharpe_ratio"], index=False)
            print("Trades successfully saved to CSV.")
        except Exception as e:
            print(f"Failed to save trades: {e}")

    def record_trade_user_input(self):
        try:
            price_t1 = float(input("Enter entry price: "))
            quantity = int(input("Enter quantity: "))
            price_t2 = float(input("Enter exit price: "))
            
            self.record_trade(price_t1, quantity, price_t2)
            print("Trade recorded successfully.")
        except ValueError:
            print("Invalid input. Please enter numeric values for price and integer for quantity.")

    def calculate_win_rate(self):
        self.trades['win'] = self.trades['profit'] > 0
        return self.trades.groupby(self.trades.time.dt.hour)['win'].mean()

    def update_kelly_fraction(self):
        recent_trades = self.trades.tail(5)
        if not recent_trades.empty:
            wins = recent_trades[recent_trades['profit'] > 0]
            losses = recent_trades[recent_trades['profit'] <= 0]
            win_rate = len(wins) / len(recent_trades) if len(recent_trades) > 0 else 0
            avg_win = wins['profit'].mean() if not wins.empty else 0
            avg_loss = losses['profit'].abs().mean() if not losses.empty else 0
            b = avg_win / avg_loss if avg_loss != 0 else 0
            self.kelly_fraction = (win_rate - ((1 - win_rate) / b)) if b != 0 else 0
            self.kelly_fraction = max(0, min(self.kelly_fraction, 1)) * 0.5
        else:
            self.kelly_fraction = 0  # Default or fallback value if not enough data
        # Update DataFrame to include new Kelly fraction
        self.trades.loc[self.trades.index[-1], 'kelly_fraction'] = self.kelly_fraction
        self.save_trades()

    def calculate_performance_metrics(self):
        if not self.trades.empty:
            returns = self.trades['profit'] / self.bankroll
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(len(self.trades)) if returns.std() != 0 else float('inf')
            # Update the entire DataFrame or just the last entry as needed
            self.trades['sharpe_ratio'] = sharpe_ratio  # This assumes updating all rows, adjust as necessary
            self.save_trades()

if __name__ == "__main__":
    tp = TradingProgram()
    tp.record_trade_user_input()
