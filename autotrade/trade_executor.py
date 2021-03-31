import logging
import math
import time
from datetime import datetime, timezone
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
        sell_list = self.__filter_stocks_against_positions(sell_list, True)
        self.update_positions(sell_list)

        # Wait 1 min from updating before proceeding to buy
        time_to_sleep = 60
        log.info(
            'Done updating positions, waiting %s seconds...', time_to_sleep)
        time.sleep(time_to_sleep)

        # 2 Buy stocks as signaled (only if not already holding)
        buy_list = [stock for stock in stock_list if (
            stock['advice'] == 'BUY')]
        buy_list = self.__filter_stocks_against_positions(buy_list, False)
        buy_list = self.__filter_stocks_against_orders(buy_list)
        self.buy(buy_list)

    def update_positions(self, sell_list: List[dict]) -> None:
        open_positions = self.account_manager.open_positions()
        if open_positions:
            log.info('Updating current positions')
            api = self.session_handler.api()
            for position in open_positions:
                symbol = position.symbol
                qty = int(position.qty)
                unrealized_plpc = float(position.unrealized_plpc)
                sell_signal = False
                for stock in sell_list:
                    if stock['ticker'] == symbol:
                        sell_signal = True
                    break
                # TODO Must handle potential holding orders before selling
                if sell_signal or (unrealized_plpc >= (self.account_manager.take_profit_pc / 100) or unrealized_plpc <= -(self.account_manager.stop_loss_pc / 100)):
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
            current_orders = api.list_orders()
            for stock in buy_list:
                signal = str.lower(stock['advice'])
                symbol = stock['ticker']
                # Check eligibility before each attempted trade
                # Conditions may have changed since last order was put
                if not self.account_manager.is_eligible_for_trading():
                    log.warn('Account is not eligable for further trading')
                    break
                # Check for any outstanding orders on stock, don't place order if so
                already_held_order = False
                for order in current_orders:
                    if order.symbol == symbol:
                        log.info(
                            'Already holding order for %s, will not place new. Current order: %s', symbol, order)
                        already_held_order = True
                        break
                if already_held_order:
                    continue
                else:
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

    def __filter_stocks_against_positions(self, stock_list: List[dict], holding_position: bool) -> List[dict]:
        """
        Check whether or not a position for a stock in a list is held in current portfolio
        """
        open_positions = self.account_manager.open_positions()
        if open_positions:
            filtered_list = []
            for stock in stock_list:
                holding_pos = holding_position
                for pos in open_positions:
                    if stock['ticker'] == pos.symbol:
                        holding_pos = not holding_pos
                        continue
                if not holding_pos:
                    filtered_list.append(stock)
            return filtered_list
        else:
            return stock_list

    def __filter_stocks_against_orders(self, stock_list: List[dict]) -> List[dict]:
        """
        Check if there are active orders for a stock in provided stock list
        """
        today = datetime.today().replace(tzinfo=timezone.utc).date()
        # FIX: Is there something wrong with 'status' param of list_orders()?
        orders = self.account_manager.orders(status='nn')
        if orders:
            filtered_list = []
            for stock in stock_list:
                for order in orders:
                    live_order = False
                    # TODO Temporary/necessary due to issues in updated trading data from API
                    # Remove once API is updated/improved with live data
                    oca = order.created_at
                    oca_date = datetime(oca.year, oca.month, oca.day).date()
                    if stock['ticker'] == order.symbol and oca_date == today:
                        log.info(
                            'Already traded %s today (%s), will not trade again', stock['ticker'], today)
                        live_order = True
                        continue
                    if stock['ticker'] == order.symbol and (order.status == 'new' or order.status == 'held'):
                        # Order has already been placed. Don't trade again (for simplicity atm).
                        log.info(
                            'Already holding at least one order for %s today (%s), will not add any more', stock['ticker'], today)
                        live_order = True
                        continue
                    if not live_order:
                        filtered_list.append(stock)
            return filtered_list
        else:
            return stock_list

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
