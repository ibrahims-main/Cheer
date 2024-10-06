class EconomyErrors(Exception):
    pass

class AccountNotFound(EconomyErrors):
    def __init__(self, message="Account not found. Please create one first"):
        self.message = message
        super().__init__(self.message)

class InsufficientFunds(EconomyErrors):
    def __init__(self, message="Insufficient funds to perform the requested action"):
        self.message = message
        super().__init__(self.message)

class InvalidAmount(EconomyErrors):
    def __init__(self, message="Invalid amount provided"):
        self.message = message
        super().__init__(self.message)

class ItemNotFound(EconomyErrors):
    def __init__(self, message="Item not found in the shop or inventory"):
        self.message = message
        super().__init__(self.message)