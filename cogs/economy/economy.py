import discord
import sqlite3
import asyncio
from discord.ext import commands
from discord import app_commands
from utils.other.economy_errors import AccountNotFound, InsufficientFunds, InvalidAmount, ItemNotFound
from typing import List, Tuple

class EconomyDB:
    def __init__(self):
        self.db = sqlite3.connect("utils/database/economy.db")
        self.cur = self.db.cursor()
        self.create_economyDB()
        self.create_loansDB()
        self.create_shopItemsDB()
        self.create_userAssetsDB()

    def create_economyDB(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER PRIMARY KEY,
                wallet INTEGER,
                bank INTEGER
            )
        """)
        self.db.commit()

    def create_loansDB(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS active_loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debtor_id INTEGER,
                lender_id INTEGER,
                amount INTEGER,
                status TEXT, -- "pending", "repaid"
                FOREIGN KEY (debtor_id) REFERENCES economy(user_id),
                FOREIGN KEY (lender_id) REFERENCES economy(user_id)
            )
        """)
        self.db.commit()

    def create_shopItemsDB(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS shop_items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price INTEGER NOT NULL
            )
        """)
        self.db.commit()

    def create_userAssetsDB(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS user_assets (
                user_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES economy(user_id),
                FOREIGN KEY (item_id) REFERENCES shop_items(id)
            )
        """)
        self.db.commit()

    def close(self):
        self.db.close()

class Shop:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.items_per_page = 5

    def shop_items(self) -> List[Tuple[str, int]]:
        return [
            ("Health Potion", 50),
            ("Mana Potion", 40),
            ("Stamina Potion", 30),
            ("Energy Drink", 20),
            ("Food Ration", 15),
            ("Magic Elixir", 100),
            ("Super Health Potion", 150),
            ("Revive Potion", 200),
            ("Wooden Sword", 80),
            ("Iron Sword", 150),
            ("Steel Axe", 200),
            ("Magic Wand", 250),
            ("Bow and Arrows", 300),
            ("Crossbow", 350),
            ("Dagger", 100),
            ("Battle Axe", 400),
            ("Leather Armor", 120),
            ("Chainmail Armor", 250),
            ("Plate Armor", 400),
            ("Mage Robe", 200),
            ("Ring of Strength", 250),
            ("Amulet of Wisdom", 300),
            ("Boots of Speed", 200),
            ("Cloak of Invisibility", 400),
            ("Pickaxe", 100),
            ("Axe", 80),
            ("Shovel", 50),
            ("Hammer", 60),
            ("Crafting Table", 120),
            ("Wood Plank", 10),
            ("Iron Ore", 30),
            ("Gold Ore", 50),
            ("Diamond", 100),
            ("Enchanted Gem", 250),
            ("Treasure Map", 200),
            ("Mystic Scroll", 300),
            ("Potion of Time", 500),
            ("Crystal Ball", 400),
            ("Magic Mirror", 350),
            ("Ancient Artifact", 800),
            ("Dragon Egg", 1000),
            ("Dog Companion", 150),
            ("Cat Companion", 120),
            ("Magical Owl", 300),
            ("Dragonling", 500),
            ("Unicorn", 700),
            ("Horse", 400),
            ("Magic Carpet", 600),
            ("Boat", 300),
            ("Airship", 1000),
            ("Bicycle", 200),
            ("Wooden Table", 100),
            ("Chair", 50),
            ("Bed", 200),
            ("Bookshelf", 150),
            ("Decorative Plant", 30),
            ("Painting", 80),
            ("Fireplace", 300),
            ("Lantern", 40),
            ("Map of the Realm", 50),
            ("Spyglass", 150),
            ("Notebook", 25),
            ("Quill and Ink", 20),
            ("Timekeeper (watch)", 250),
            ("Music Box", 300),
            ("Mirror of Truth", 400),
            ("Christmas Tree", 500),
            ("Halloween Costume", 300),
            ("Fireworks", 100),
            ("New Year’s Party Hat", 200),
            ("Easter Egg", 150),
            ("Staff of Fire", 500),
            ("Cloak of Shadows", 600),
            ("Boots of Levitation", 700),
            ("Amulet of the Gods", 800),
            ("Crystal Staff", 900),
            ("Rare Coin", 100),
            ("Vintage Card", 50),
            ("Comic Book", 80),
            ("Action Figure", 120),
            ("Signed Memorabilia", 200),
            ("Joke Book", 25),
            ("Board Game", 70),
            ("Puzzle", 30),
            ("Magic 8 Ball", 40),
            ("Rubber Chicken", 10),
            ("Smartphone", 300),
            ("Laptop", 800),
            ("Gaming Console", 500),
            ("VR Headset", 600),
            ("Smartwatch", 400),
            ("Hat", 80),
            ("Sunglasses", 100),
            ("Jacket", 150),
            ("Shoes", 200),
            ("Dress", 300),
            ("Stuffed Animal", 50),
            ("Action Figure", 70),
            ("Toy Car", 30),
            ("Puzzle Toy", 20),
            ("Building Blocks", 40),
        ]

    async def show_shop(self, interaction: discord.Interaction, page: int = 0):
        """Handles pagination of the shop items."""
        items = self.shop_items()
        start = page * self.items_per_page
        end = start + self.items_per_page
        shop_page = items[start:end]
        
        embed = discord.Embed(title="Shop Items", color=discord.Color.green())
        for item in shop_page:
            embed.add_field(name=item[0], value=f"Price: {item[1]} :)'s", inline=False)

        view = discord.ui.View()
        if page > 0:
            prev_button = discord.ui.Button(label="Previous", style=discord.ButtonStyle.primary)
            prev_button.callback = lambda i: asyncio.ensure_future(self.show_shop(i, page - 1))
            view.add_item(prev_button)
        
        if end < len(items):
            next_button = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary)
            next_button.callback = lambda i: asyncio.ensure_future(self.show_shop(i, page + 1))
            view.add_item(next_button)

        await interaction.response.send_message(embed=embed, view=view)

class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.economy = EconomyDB()
        self.shop = Shop()

    """
    Account Management
    """

    async def check_account(self, user_id: int, interaction: discord.Interaction) -> bool:
        self.economy.cur.execute("SELECT * FROM economy WHERE user_id = ?", (user_id,))
        result = self.economy.cur.fetchone()

        if result:
            return True
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention}, you do not have an account! Please create one by using the `/setup` command.", 
                ephemeral=True
            )
            return False

    @app_commands.command(name="setup", description="Setup your account")
    async def setup(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        try:
            if await self.check_account(user_id):
                raise AccountNotFound()

            self.economy.cur.execute("INSERT INTO economy (user_id, wallet, bank) VALUES (?, 100, 0)", (user_id,))
            self.economy.db.commit()
            await interaction.response.send_message(
                f"{interaction.user.mention}, your account has been set up with a default balance of 100 in your wallet!"
            )
        except AccountNotFound as e:
            await interaction.response.send_message(e.message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occurred while setting up your account. Please try again later.", ephemeral=True)

    @app_commands.command(name="deleteaccount", description="Delete your economy account")
    async def deleteaccount(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        try:
            if not await self.check_account(user_id):
                raise AccountNotFound()

            self.economy.cur.execute("DELETE FROM economy WHERE user_id=?", (user_id,))
            self.economy.db.commit()
            await interaction.response.send_message(f"{interaction.user.mention}, your account has been deleted.")
        except AccountNotFound as e:
            await interaction.response.send_message(e.message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occurred while deleting your account. Please try again later.", ephemeral=True)

    @app_commands.command(name="resetaccount", description="Reset your economy account")
    async def resetaccount(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        try:
            if not await self.check_account(user_id):
                raise AccountNotFound()

            self.economy.cur.execute("UPDATE economy SET wallet=100, bank=0 WHERE user_id=?", (user_id,))
            self.economy.db.commit()
            await interaction.response.send_message(
                f"{interaction.user.mention}, your account has been reset to a default balance of 100 in your wallet."
            )
        except AccountNotFound as e:
            await interaction.response.send_message(e.message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occurred while resetting your account. Please try again later.", ephemeral=True)

    @app_commands.command(name="checkaccount", description="Check your account")
    async def checkaccount(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        try:
            if not await self.check_account(user_id):
                raise AccountNotFound()

            await interaction.response.send_message("You have an economy account!")
        except AccountNotFound as e:
            await interaction.response.send_message(e.message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occurred while checking your account. Please try again later.", ephemeral=True)

    @app_commands.command(name="accountinfo", description="Displays your or another user's account information")
    async def accountinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        user_id = user.id

        try:
            self.economy.cur.execute("SELECT wallet, bank FROM economy WHERE user_id=?", (user_id,))
            account = self.economy.cur.fetchone()

            if account:
                wallet, bank = account
                embed = discord.Embed(
                    title=f"{user}'s Account Info",
                    description=f"Wallet Balance: {wallet} \nBank Balance: {bank}",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)
            else:
                raise AccountNotFound()
        except AccountNotFound as e:
            await interaction.response.send_message(e.message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occurred while retrieving account information. Please try again later.", ephemeral=True)

    """
    Balance Checks
    """

    @app_commands.command(name="wallet", description="Shows you your wallet balance")
    async def wallet(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        try:
            if not await self.check_account(user_id):
                raise AccountNotFound()

            self.economy.cur.execute("SELECT wallet FROM economy WHERE user_id=?", (user_id,))
            wallet = self.economy.cur.fetchone()[0]

            embed = discord.Embed(
                title="Wallet Balance",
                description=f"Your wallet balance is: {wallet}",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
        except AccountNotFound as e:
            await interaction.response.send_message(e.message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("An error occurred while retrieving your wallet balance. Please try again later.", ephemeral=True)

    @app_commands.command(name="bank", description="Shows you your bank balance")
    async def bank(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if not await self.check_account(user_id):
            raise AccountNotFound()

        self.economy.cur.execute("SELECT bank FROM economy WHERE user_id=?", (user_id,))
        result = self.economy.cur.fetchone()

        if result is None:
            raise AccountNotFound()

        bank = result[0]

        embed = discord.Embed(
            title="Bank Balance",
            description=f"Your bank balance is: {bank}",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="networth", description="Check your total net worth (wallet + bank + assets)")
    async def networth(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        # Fetch wallet and bank balances
        self.economy.cur.execute("SELECT wallet, bank FROM economy WHERE user_id=?", (user_id,))
        result = self.economy.cur.fetchone()

        if not result:
            await interaction.response.send_message("Account not found.", ephemeral=True)
            return

        wallet, bank = result

        # Fetch asset values
        self.economy.cur.execute("SELECT SUM(s.price * ua.quantity) FROM user_assets ua JOIN shop_items s ON ua.item_id = s.id WHERE ua.user_id = ?", (user_id,))
        asset_value = self.economy.cur.fetchone()[0] or 0

        net_worth = wallet + bank + asset_value
        await interaction.response.send_message(f"{interaction.user.mention}, your total net worth is: {net_worth} :)'s.")

    @app_commands.command(name="richest", description="List the top richest users in the server")
    async def richest(self, interaction: discord.Interaction):
        self.economy.cur.execute("SELECT user_id, wallet + bank AS total FROM economy ORDER BY total DESC LIMIT 10")
        top_rich = self.economy.cur.fetchall()

        if not top_rich:
            await interaction.response.send_message("No users found.")
            return

        embed = discord.Embed(title="Top Richest Users", color=discord.Color.gold())
        for index, (user_id, total) in enumerate(top_rich, start=1):
            user = await self.bot.fetch_user(user_id)
            embed.add_field(name=f"{index}. {user}", value=f"Total: {total} :)'s", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poorest", description="List the top poorest users in the server")
    async def poorest(self, interaction: discord.Interaction):
        self.economy.cur.execute("SELECT user_id, wallet + bank AS total FROM economy ORDER BY total ASC LIMIT 10")
        top_poor = self.economy.cur.fetchall()

        if not top_poor:
            await interaction.response.send_message("No users found.")
            return

        embed = discord.Embed(title="Top Poorest Users", color=discord.Color.red())
        for index, (user_id, total) in enumerate(top_poor, start=1):
            user = await self.bot.fetch_user(user_id)
            embed.add_field(name=f"{index}. {user}", value=f"Total: {total} :)'s", inline=False)
        await interaction.response.send_message(embed=embed)

    """
    Transactions
    """

    @app_commands.command(name="deposit", description="Deposits money into your bank")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        user_id = interaction.user.id

        if not await self.check_account(user_id):
            raise AccountNotFound()

        self.economy.cur.execute("SELECT wallet FROM economy WHERE user_id=?", (user_id,))
        wallet_balance = self.economy.cur.fetchone()

        if wallet_balance is None:
            raise AccountNotFound()  # Handle case where account exists but no wallet balance found

        wallet_balance = wallet_balance[0]

        if wallet_balance >= amount > 0:
            self.economy.cur.execute(
                "UPDATE economy SET wallet = wallet - ?, bank = bank + ? WHERE user_id = ?",
                (amount, amount, user_id)
            )
            self.economy.db.commit()
            await interaction.response.send_message(f"Deposited {amount} into your bank.")
        else:
            raise InsufficientFunds()

    @app_commands.command(name="withdraw", description="Withdraw money from your bank")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        user_id = interaction.user.id

        if not await self.check_account(user_id):
            raise AccountNotFound()

        self.economy.cur.execute("SELECT bank FROM economy WHERE user_id=?", (user_id,))
        bank_balance = self.economy.cur.fetchone()

        if bank_balance is None:
            raise AccountNotFound()  # Handle case where account exists but no bank balance found

        bank_balance = bank_balance[0]

        if bank_balance >= amount > 0:
            self.economy.cur.execute(
                "UPDATE economy SET wallet = wallet + ?, bank = bank - ? WHERE user_id = ?",
                (amount, amount, user_id)
            )
            self.economy.db.commit()
            await interaction.response.send_message(f"Withdrew {amount} from your bank.")
        else:
            raise InsufficientFunds()
        
    @app_commands.command(name="transfer", description="Transfer money to another user")
    async def transfer(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        user_id = interaction.user.id
        target_user_id = user.id

        if not await self.check_account(user_id, interaction):
            return

        self.economy.cur.execute("SELECT wallet FROM economy WHERE user_id=?", (user_id,))
        result = self.economy.cur.fetchone()

        if result is None:
            raise AccountNotFound()  # Handle case where account does not exist

        wallet_balance = result[0]

        if wallet_balance >= amount > 0:
            if await self.check_account(target_user_id):  # Check if the target user has an account
                self.economy.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (amount, user_id))
                self.economy.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (amount, target_user_id))
                self.economy.db.commit()
                await interaction.response.send_message(f"Transferred {amount} :)'s to {user.mention}.")
            else:
                raise AccountNotFound(f"Target user {user.mention} does not have an account.")
        else:
            raise InsufficientFunds()
        
    @app_commands.command(name="gift", description="Gift money to another user")
    async def gift(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        user_id = interaction.user.id
        target_user_id = user.id

        if not await self.check_account(user_id, interaction):
            return

        self.economy.cur.execute("SELECT wallet FROM economy WHERE user_id=?", (user_id,))
        result = self.economy.cur.fetchone()

        if result is None:
            raise AccountNotFound()  # Handle case where the account does not exist

        wallet_balance = result[0]

        if wallet_balance >= amount > 0:
            if await self.check_account(target_user_id):  # Check if the target user has an account
                self.economy.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (amount, user_id))
                self.economy.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (amount, target_user_id))
                self.economy.db.commit()
                await interaction.response.send_message(f"Gave {amount} :)'s to {user.mention} as a gift.")
            else:
                raise AccountNotFound(f"Target user {user.mention} does not have an account.")
        else:
            raise InsufficientFunds()

    @app_commands.command(name="giveaway", description="Start a giveaway for a specified amount")
    async def giveaway(self, interaction: discord.Interaction, amount: int):
        if amount <= 0:
            await interaction.response.send_message("The giveaway amount must be greater than zero.")
            return

        embed = discord.Embed(
            title="Giveaway!",
            description=f"React with 🎉 to enter for a chance to win {amount} :)'s!",
            color=discord.Color.green()
        )

        message = await interaction.response.send_message(embed=embed)
        await message.add_reaction("🎉")

        def check(reaction, user):
            return reaction.emoji == "🎉" and not user.bot

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

            # Winner selection logic
            if await self.check_account(user.id):  # Check if the winner has an account
                self.economy.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (amount, user.id))
                self.economy.db.commit()
                await interaction.channel.send(f"Congratulations {user.mention}! You won {amount} :)'s!")
            else:
                await interaction.channel.send(f"Winner {user.mention} does not have an economy account, so no prize will be given.")
        except asyncio.TimeoutError:
            await interaction.channel.send("Giveaway ended! No winner.")

    @app_commands.command(name="loan", description="Request a loan from another user")
    async def loan(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        debtor_id = interaction.user.id
        lender_id = user.id

        if not await self.check_account(debtor_id, interaction):
            return

        self.economy.cur.execute("SELECT wallet FROM economy WHERE user_id=?", (debtor_id,))
        debtor_wallet = self.economy.cur.fetchone()

        if debtor_wallet and debtor_wallet[0] < amount:
            raise InsufficientFunds()

        # Insert loan into active_loans table
        self.economy.cur.execute("""
            INSERT INTO active_loans (debtor_id, lender_id, amount, status)
            VALUES (?, ?, ?, 'pending')
        """, (debtor_id, lender_id, amount))
        
        self.economy.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (amount, debtor_id))
        self.economy.db.commit()

        await interaction.response.send_message(f"You have requested a loan of {amount} :)'s from {user.mention}.")


    @app_commands.command(name="repay", description="Repay a loan to another user")
    async def repay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        debtor_id = interaction.user.id
        lender_id = user.id

        if not await self.check_account(debtor_id, interaction):
            return

        # Check if the user has an active loan
        self.economy.cur.execute("SELECT amount FROM active_loans WHERE debtor_id = ? AND lender_id = ? AND status = 'pending'", (debtor_id, lender_id))
        loan = self.economy.cur.fetchone()

        if loan is None:
            await interaction.response.send_message("You do not have an active loan from this user.")
            return

        # Check if the amount to repay is valid
        self.economy.cur.execute("SELECT wallet FROM economy WHERE user_id=?", (debtor_id,))
        result = self.economy.cur.fetchone()

        if result:
            wallet_balance = result[0]

            if wallet_balance < amount or amount <= 0:
                raise InsufficientFunds()

            # Deduct the amount from the debtor and add it to the lender
            self.economy.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (amount, debtor_id))
            self.economy.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (amount, lender_id))
            
            # Check if the repayment clears the loan
            remaining_loan = loan[0] - amount
            if remaining_loan <= 0:
                # Mark loan as repaid if fully repaid
                self.economy.cur.execute("UPDATE active_loans SET status = 'repaid' WHERE debtor_id = ? AND lender_id = ?", (debtor_id, lender_id))
            else:
                # Update the loan amount remaining
                self.economy.cur.execute("UPDATE active_loans SET amount = ? WHERE debtor_id = ? AND lender_id = ?", (remaining_loan, debtor_id, lender_id))

            self.economy.db.commit()
            await interaction.response.send_message(f"Repayed {amount} :)'s to {user.mention}.")

    @app_commands.command(name="shop", description="Browse the shop items")
    async def shop(self, interaction: discord.Interaction):
        await self.shop.show_shop(interaction)

    @commands.command(name="buy", description="Buy an item from the shop")
    async def buy(self, interaction: discord.Interaction, item_name: str, quantity: int):
        user_id = interaction.user.id

        # Fetch item from shop
        items = self.shop.shop_items()  # Assuming `self.shop` is the instance of Shop class
        item = next((i for i in items if i[0].lower() == item_name.lower()), None)

        if not item:
            raise ItemNotFound()

        item_name, price = item
        total_cost = price * quantity

        # Fetch wallet balance
        self.economy.cur.execute("SELECT wallet FROM economy WHERE user_id=?", (user_id,))
        wallet_balance = self.economy.cur.fetchone()[0]

        if wallet_balance < total_cost:
            raise InsufficientFunds()

        # Update user's assets and wallet
        self.economy.cur.execute(
            "INSERT INTO user_assets (user_id, item_id, quantity) VALUES (?, ?, ?) ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + ?",
            (user_id, item[0], quantity, quantity)
        )
        self.economy.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (total_cost, user_id))
        self.economy.db.commit()

        await interaction.response.send_message(f"Bought {quantity} {item_name}(s) for {total_cost} :)'s.")

    @commands.command(name="sell", description="Sell an item from your assets")
    async def sell(self, interaction: discord.Interaction, item_name: str, quantity: int):
        user_id = interaction.user.id

        # Fetch item from shop
        items = self.shop.shop_items()  # Assuming `self.shop` is the instance of Shop class
        item = next((i for i in items if i[0].lower() == item_name.lower()), None)

        if not item:
            raise ItemNotFound()

        item_name, price = item

        # Fetch user assets
        self.economy.cur.execute("SELECT quantity FROM user_assets WHERE user_id = ? AND item_id = ?", (user_id, item_name))
        result = self.economy.cur.fetchone()

        if not result or result[0] < quantity:
            raise InvalidAmount("You don't have enough of that item to sell.")

        # Update assets and wallet
        self.economy.cur.execute("UPDATE user_assets SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_name))
        self.economy.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (quantity * price, user_id))
        self.economy.db.commit()

        await interaction.response.send_message(f"Sold {quantity} {item_name}(s).")

    @app_commands.command(name="assets", description="View your assets")
    async def assets(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        # Fetch user assets
        self.economy.cur.execute("SELECT item_name, quantity FROM user_assets WHERE user_id = ?", (user_id,))
        assets = self.economy.cur.fetchall()

        if not assets:
            await interaction.response.send_message("You have no assets.", ephemeral=True)
            return

        embed = discord.Embed(title="Your Assets", color=discord.Color.blue())
        for name, quantity in assets:
            embed.add_field(name=name, value=f"Quantity: {quantity}", inline=False)

        await interaction.response.send_message(embed=embed)

    """
    Error Handlers
    """

    @deleteaccount.error
    @resetaccount.error
    @checkaccount.error
    @wallet.error
    @bank.error
    @deposit.error
    @withdraw.error
    @networth.error
    @richest.error
    @poorest.error
    @transfer.error
    @gift.error
    @giveaway.error
    @loan.error
    @repay.error
    @shop.error
    @buy.error
    @sell.error
    @assets.error
    async def account_error_handler(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, AccountNotFound):
            await interaction.response.send_message(error.message, ephemeral=True)
        elif isinstance(error, InsufficientFunds):
            await interaction.response.send_message(error.message, ephemeral=True)
        elif isinstance(error, InvalidAmount):
            await interaction.response.send_message(error.message, ephemeral=True)
        elif isinstance(error, ItemNotFound):
            await interaction.response.send_message(error.message, ephemeral=True)
        else:
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)

    def cog_unload(self):
        self.economy.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))