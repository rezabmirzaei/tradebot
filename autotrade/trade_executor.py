import logging
import math
import time
from typing import List

import alpaca_trade_api as tradeapi
import yfinance as yf

from autotrade.account_manager import AccountManager
from autotrade.session_handler import SessionHandler

log = logging.getLogger('tradebot.log')


class TradeExecutor():

    def __init__(self, session_handler: SessionHandler, account_manager: AccountManager) -> None:
        self.session_handler: SessionHandler = session_handler
        self.account_manager: AccountManager = account_manager

    def run(self, stock_list: List[dict]) -> None:

        # TODO Notify if issues (email/sms)
        # Check more conditions, e.g. PDT, market open etc.
        if not self.account_manager.is_eligible_for_trading():
            log.warn('Account is not eligable for trading')
            return

        log.info('Running trades')

        # 1 Update current status of portfolio, sell if certain conditions are met
        sell_list = [
            stock for stock in stock_list if stock['advice'] == 'SELL']
        self.update_positions(sell_list)

        # Wait 1 min from updating before proceeding to buy
        time_to_sleep = 60
        log.info(
            'Done updating positions, waiting %s seconds...', time_to_sleep)
        time.sleep(time_to_sleep)

        # 2 Buy stocks as signaled (only if not already holding)
        open_positions = self.account_manager.open_positions()
        buy_list = [stock for stock in stock_list if (
            stock['advice'] == 'BUY')]
        # TODO Write a function for this
        if open_positions:
            filtered_buy = []
            for stock in buy_list:
                holding_pos = False
                for pos in open_positions:
                    if stock['ticker'] == pos.symbol:
                        holding_pos = True
                        continue
                if not holding_pos:
                    filtered_buy.append(stock)
            self.buy(filtered_buy)
        else:
            self.buy(buy_list)

    def update_positions(self, sell_list: List[dict]) -> None:
        open_positions = self.account_manager.open_positions()
        # TODO FIX THIS FILTER!!! Stupid thing doesn't work!!!
        sell_positions = [pos for pos, stock in zip(open_positions, sell_list) if (
            stock['advice'] == 'SELL' and pos.symbol == stock['ticker'])]
        if open_positions:
            log.info('Updating current positions')
            api = self.session_handler.api()
            for position in open_positions:
                symbol = position.symbol
                qty = int(position.qty)
                unrealized_plpc = float(position.unrealized_plpc)
                # TODO Consider this condition, handle different scenarios
                # if unrealized_plpc > (self.account_manager.take_profit_pc / 100):
                # TODO Get all open orders related to current open position and handle them
                # TODO TESTING only
                if position in sell_positions or (unrealized_plpc >= 0.07 or unrealized_plpc <= -0.05):
                    log.info('Selling %s shares of %s (profit: %s)',
                             qty, symbol, unrealized_plpc)
                    try:
                        api.submit_order(
                            symbol=symbol,
                            side='sell',
                            qty=qty,
                            type='market',
                            time_in_force='day')
                    except Exception as e:
                        log.error('Error placing sell order: %s', str(e))
                        continue
        else:
            log.info('No open positions to update')

    def buy(self, buy_list: List[dict]) -> None:
        if buy_list:
            log.info('Buying stocks as signaled')
            api = self.session_handler.api()
            for stock in buy_list:
                signal = str.lower(stock['advice'])
                symbol = stock['ticker']
                # Check eligibility before each attempted trade
                # Conditions may have changed since last order was put
                # TODO Make sure market isn't near close
                if not self.account_manager.is_eligible_for_trading():
                    log.warn('Account is not eligable for further trading')
                    break
                try:
                    order_details = self.__buy_order_details(stock)
                    if order_details:
                        log.info('Buying %s. Order details: %s',
                                 symbol, order_details)
                        api.submit_order(
                            symbol=symbol,
                            side=signal,
                            qty=order_details['qty'],
                            type='market',
                            time_in_force='gtc',
                            order_class='bracket',
                            take_profit=dict(
                                limit_price=order_details['take_profit']
                            ),
                            stop_loss=dict(
                                stop_price=order_details['stop_loss']
                            )
                        )
                except Exception as e:
                    log.error('Error placing buy order: %s', str(e))
                    continue
        else:
            log.info('Nothing to buy')

    def __buy_order_details(self, stock: dict) -> dict:
        symbol = stock['ticker']
        stock_info = yf.download(symbol, period='2min')
        latest_adj_close = round(stock_info['Adj Close'][-1], 2)
        investment_pc = self.account_manager.investment_pc
        take_profit_pc = self.account_manager.take_profit_pc
        stop_loss_pc = self.account_manager.stop_loss_pc
        account_details = self.account_manager.account_details()
        buying_power = float(account_details.buying_power)
        amount_to_invest = buying_power * (investment_pc / 100)
        qty = math.floor(amount_to_invest / latest_adj_close)
        if qty == 0:
            log.warn(
                'Cannot create order for %s due to insufficent funds', symbol)
            return None
        take_profit = round(latest_adj_close *
                            (1 + take_profit_pc / 100), 2)
        stop_loss = round(latest_adj_close *
                          (1 - stop_loss_pc / 100), 2)
        order_details = {
            'symbol': symbol,
            'qty': qty,
            'limit': latest_adj_close,
            'take_profit': take_profit,
            'stop_loss': stop_loss
        }
        return order_details
