"""
Errors Class
"""

class EconomyErrors(Exception):
    pass

class NoActiveLoan(EconomyErrors):
    def __init__(self, message="You have no active loans to repay"):
        self.message = message
        super().__init__(self.message)

class InsufficientFunds(EconomyErrors):
    def __init__(self, message="You don't have enough funds to repay the loan."):
        self.message = message
        super().__init__(self.message)