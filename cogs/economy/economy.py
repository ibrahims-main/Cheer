import sqlite3
from asyncio import TimeoutError, ensure_future
from discord.ext import commands
from discord import app_commands, Interaction, Member, Embed, Color, utils, Message, ButtonStyle, ui
from typing import Optional, List, Tuple
from utils.other.economy_errs import *

class EconomyDB:
    def __init__(self):
        self.db = sqlite3.connect("utils/database/economy.db")
        self.cur = self.db.cursor()
        
        self.create_economyDB()
        self.create_loansDB()
        self.create_userAssetsDB()

    def create_economyDB(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER PRIMARY KEY,
                wallet INTEGER DEFAULT 100,
                bank INTEGER DEFAULT 0
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

    def create_userAssetsDB(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS user_assets (
                user_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES economy(user_id),
            )
        """)
        self.db.commit()
    
    """
    Loans Checks
    """
    
    def get_active_loan(self, user_id: int):
        self.cur.execute("SELECT id, amount FROM active_loans WHERE debtor_id = ? AND status = 'pending'", (user_id,))
        return self.cur.fetchone()

    def repay_loan(self, loan_id: int, amount: int):
        self.cur.execute("UPDATE active_loans SET amount = amount - ? WHERE id = ?", (amount, loan_id))
        self.db.commit()

    def mark_loan_repaid(self, loan_id: int):
        self.cur.execute("UPDATE active_loans SET status = 'repaid' WHERE id = ?", (loan_id,))
        self.db.commit()

    """
    Close the Database
    """

    def close(self):
        self.db.close()

class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = EconomyDB()
        self.items_per_page = 5

    """
    Check Functions
    """

    def check_account(self, user_id: int):
        self.db.cur.execute("SELECT * FROM economy WHERE user_id = ?", (user_id,))
        return self.db.cur.fetchone()
    
    def check_balance(self, balance: int, amount: int) -> bool:
        return balance >= amount > 0

    """
    Account Management
    """

    @app_commands.command(name="createaccount", description="Create your economy account")
    async def createaccount(self, interaction: Interaction):
        user_id = interaction.user.id
        account = self.check_account(user_id)

        if account:
            return await interaction.response.send_message("You already have an economy account.", ephemeral=True)
        
        self.db.cur.execute("INSERT INTO economy (user_id, wallet, bank) VALUES (?, 100, 0)", (user_id,))
        self.db.db.commit()
        await interaction.response.send_message(f"{interaction.user.mention}, your account has been set up with a default balance of 100 :) in your wallet!")

    @app_commands.command(name="accountinfo", description="View yours or someone else's balance/info")
    async def accountinfo(self, interaction: Interaction, user: Optional[Member] = None):
        user = user or interaction.user
        user_id = user.id

        account = self.check_account(user_id)

        if account:
            wallet, bank = account[1], account[2]
            
            self.db.cur.execute("SELECT item_id, quantity FROM user_assets WHERE user_id = ?", (user_id,))
            user_assets = self.db.cur.fetchall()

            asset_details = []
            for item_id, quantity in user_assets:
                self.db.cur.execute("SELECT name, price FROM shop_items WHERE id = ?", (item_id,))
                item_info = self.db.cur.fetchone()
                if item_info:
                    item_name, item_price = item_info
                    asset_details.append(f"{item_name} (x{quantity}): {item_price} :)'s each")

            asset_string = "\n".join(asset_details) if asset_details else "No assets owned."

            embed = Embed(
                title=f"{user.display_name}'s Economy Account",
                description=f"**Wallet:** {wallet}\n**Bank:** {bank}\n**Assets:**\n{asset_string}",
                color=Color.blue()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

    @app_commands.command(name="deleteaccount", description="Delete your economy account")
    async def deleteaccount(self, interaction: Interaction):
        user_id = interaction.user.id
        account = self.check_account(user_id)

        if account:
            self.db.cur.execute("DELETE FROM economy WHERE user_id = ?", (user_id,))
            self.db.db.commit()
            await interaction.response.send_message(f"{interaction.user.mention}, your account has been deleted.")
        else:
            await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

    @app_commands.command(name="resetaccount", description="Reset your account (If moderator: reset someone else's account)")
    async def resetaccount(self, interaction: Interaction, user: Optional[Member] = None):
        member = user or interaction.user

        if member != interaction.user:
            role1 = utils.get(interaction.guild.roles, name="Supreme Mod Overlord")
            role2 = utils.get(interaction.guild.roles, name="God-Mode Guardian")
            role3 = utils.get(interaction.guild.roles, name=":)")

            if not any(role in interaction.user.roles for role in [role1, role2, role3]):
                await interaction.response.send_message(f"You can only reset your data; to reset other data, you must have {role1.mention}, {role2.mention}, or {role3.mention} roles", ephemeral=True)
                return
            
        member_id = member.id
        account = self.check_account(member_id)

        if account:
            self.db.cur.execute("UPDATE economy SET wallet = 100, bank = 0 WHERE user_id = ?", (member_id,))
            self.db.db.commit()
            await interaction.response.send_message(f"{member.mention}'s account has been reset.")
        else:
            await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

    """
    Balance Checks
    """

    @app_commands.command(name="wallet", description="Check your wallet balance")
    async def wallet(self, interaction: Interaction):
        user_id = interaction.user.id
        account = self.check_account(user_id)

        if account:
            wallet = account[1]
            embed = Embed(title=f"{interaction.user.display_name}'s Wallet Balance", description=f"**Wallet:** {wallet}", color=Color.green())
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

    @app_commands.command(name="bank", description="Check your bank balance")
    async def bank(self, interaction: Interaction):
        user_id = interaction.user.id
        account = self.check_account(user_id)

        if account:
            bank = account[2]
            embed = Embed(title=f"{interaction.user.display_name}'s Bank Balance", description=f"**Bank:** {bank}", color=Color.purple())
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

    @app_commands.command(name="networth", description="View your/users networth")
    async def networth(self, interaction: Interaction, user: Optional[Member] = None):
        user = user or interaction.user
        user_id = user.id
        account = self.check_account(user_id)

        if account:
            wallet, bank = account[1], account[2]
            networth = wallet + bank

            await interaction.response.send_message(
                embed=Embed(
                    title=f"{user.display_name}'s Networth",
                    description=f"{networth} :)",
                    color=Color.random()
                )
            )
        else:
            await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

    @app_commands.command(name="richest", description="List the top richest users in the server")
    async def richest(self, interaction: Interaction):
        self.db.cur.execute("SELECT user_id, wallet + bank AS total FROM economy ORDER BY total DESC LIMIT 10")
        top_rich = self.db.cur.fetchall()

        if not top_rich:
            await interaction.response.send_message("No users found.", ephemeral=True)
            return

        embed = Embed(title="Top Richest Users", color=Color.gold())
        for index, (user_id, total) in enumerate(top_rich, start=1):
            user = await self.bot.fetch_user(user_id)
            embed.add_field(name=f"{index}. {user}", value=f"Total: {total} :)'s", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poorest", description="List the top poorest users in the server")
    async def poorest(self, interaction: Interaction):
        self.db.cur.execute("SELECT user_id, wallet + bank AS total FROM economy ORDER BY total ASC LIMIT 10")
        top_poor = self.db.cur.fetchall()

        if not top_poor:
            await interaction.response.send_message("No users found.", ephemeral=True)
            return

        embed = Embed(title="Top Poorest Users", color=Color.red())
        for index, (user_id, total) in enumerate(top_poor, start=1):
            user = await self.bot.fetch_user(user_id)
            embed.add_field(name=f"{index}. {user}", value=f"Total: {total} :)'s", inline=False)
        await interaction.response.send_message(embed=embed)

    """
    Transactions
    """

    @app_commands.command(name="deposit", description="Deposit :) from your wallet to your bank")
    async def deposit(self, interaction: Interaction, amount: int):
        user_id = interaction.user.id
        account = self.check_account(user_id)

        if account:
            self.db.cur.execute("SELECT wallet FROM economy WHERE user_id = ?", (user_id,))
            wallet_balance = self.db.cur.fetchone()[0]

            if self.check_balance(wallet_balance, amount):
                self.db.cur.execute(
                    "UPDATE economy SET wallet = wallet - ?, bank = bank + ? WHERE user_id = ?",
                    (amount, amount, user_id)
                )
                self.db.db.commit()
                await interaction.response.send_message(f"Deposited {amount} into your bank.")
            else:
                await interaction.response.send_message("Sorry man but you dont have the balance for that try another amount lesser than the balance in your wallet or try depositing money from your bank to your wallet", ephemeral=True)
        else:
            await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

    @app_commands.command(name="withdraw", description="Withdraw :) from your bank to your wallet")
    async def withdraw(self, interaction: Interaction, amount: int):
        user_id = interaction.user.id
        account = self.check_account(user_id)

        if account:
            self.db.cur.execute("SELECT bank FROM economy WHERE user_id = ?", (user_id,))
            bank_balance = self.db.cur.fetchone()[0]

            if self.check_balance(bank_balance, amount):
                self.db.cur.execute(
                    "UPDATE economy SET wallet = wallet + ?, bank = bank - ? WHERE user_id = ?",
                    (amount, amount, user_id)
                )
                self.db.db.commit()
                await interaction.response.send_message(f"Withdrew {amount} from your bank.")
            else:
                await interaction.response.send_message("Sorry man but you dont have the balance for that try another amount lesser than the balance in your wallet or try depositing money from your bank to your wallet", ephemeral=True)
        else:
            await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

    @app_commands.command(name="transfer", description="Transfer :) into another user's bank")
    async def transfer(self, interaction: Interaction, user: Member, amount: int):
        user_id = interaction.user.id
        target_user_id = user.id
        user_account = self.check_account(user_id)
        target_user_account = self.check_account(target_user_id)

        if user_account and target_user_account:
            self.db.cur.execute("SELECT wallet FROM economy WHERE user_id = ?", (user_id,))
            wallet_balance = self.db.cur.fetchone()[0]
            
            if self.check_balance(wallet_balance, amount):
                self.db.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (amount, user_id,))
                self.db.cur.execute("UPDATE economy SET bank = bank + ? WHERE user_id = ?", (amount, target_user_id))
                self.db.db.commit()
                await interaction.response.send_message(f"Transferred {amount} :) to {user.display_name}'s bank.")
            else:
                await interaction.response.send_message("Sorry man but you dont have the balance for that try another amount lesser than the balance in your wallet or try depositing money from your bank to your wallet", ephemeral=True)
        elif not user_account:
            await interaction.response.send_message("Your account not found, please create one using `/createaccount`", ephemeral=True)
        elif not target_user_account:
            await interaction.response.send_message(f"{user.display_name}'s account not found.", ephemeral=True)

    @app_commands.command(name="gift", description="Gift money to another user")
    async def gift(self, interaction: Interaction, user: Member, amount: int):
        user_id = interaction.user.id
        target_user_id = user.id
        user_account = self.check_account(user_id)
        target_user_account = self.check_account(target_user_id)

        if user_account and target_user_account:
            self.db.cur.execute("SELECT wallet FROM economy WHERE user_id = ?", (user_id,))
            wallet_balance = self.db.cur.fetchone()[0]

            if self.check_balance(wallet_balance, amount):
                self.db.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (amount, user_id,))
                self.db.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (amount, target_user_id,))
                self.db.db.commit()
                await interaction.response.send_message(f"Gifted {amount} :) to {user.display_name}.", ephemeral=True)
                await user.send(f"{interaction.user.display_name} gifted you {amount} :) from their bank.")
            else:
                await interaction.response.send_message("Sorry man but you dont have the balance for that try another amount lesser than the balance in your wallet or try depositing money from your bank to your wallet", ephemeral=True)
        elif not user_account:
            await interaction.response.send_message("Your account not found, please create one using `/createaccount`", ephemeral=True)
        elif not target_user_account:
            await interaction.response.send_message(f"{user.display_name}'s account not found.", ephemeral=True)

    @app_commands.command(name="giveaway", description="Start a giveaway for a specified amount")
    async def giveaway(self, interaction: Interaction, amount: int):
        if amount <= 0:
            return await interaction.response.send_message(f"The giveaway amount must be greater than zero.", ephemeral=True)

        user_id = interaction.user.id
        account = self.check_account(user_id)
        self.db.cur.execute("SELECT wallet FROM economy WHERE user_id = ?", (user_id,))
        wallet_balance = self.db.cur.fetchone()[0]

        if account:
            if self.check_balance(wallet_balance, amount):
                embed = Embed(
                    title="Giveaway! 🎉🎉",
                    description=f"React with 🎉 to enter for a chance to win {amount} :)'s!",
                    color=Color.gold()
                )

                await interaction.response.send_message("Giveaway started!", ephemeral=True)
                message: Message = await interaction.followup.send(embed=embed, wait=True)
                await message.add_reaction("🎉")

                def check(reaction, user):
                    return reaction.emoji == "🎉" and not user.bot

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)

                    self.db.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (amount, user.id,))
                    self.db.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (amount, user_id,))
                    self.db.db.commit()

                    await interaction.followup.send(f"Congratulations {user.mention}! You've won {amount} :)'s!")
                except TimeoutError:
                    await interaction.followup.send("Giveaway timed out! No winners this time.")
            else:
                await interaction.response.send_message("Sorry, but you don't have enough balance to start a giveaway.", ephemeral=True)
        else:
            await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

    @app_commands.command(name="loan", description="Request a loan from a user")
    async def loan(self, interaction: Interaction, user: Member, amount: int):
        debtor_id = interaction.user.id
        lender_id = user.id
        debtor_account = self.check_account(debtor_id)
        lender_account = self.check_account(lender_id)

        if not lender_account:
            await interaction.response.send_message(f"{user.mention}'s account not found. They need to create one using `/createaccount`", ephemeral=True)
            return

        if not debtor_account:
            await interaction.response.send_message(f"{interaction.user.mention}'s account not found. Please create one using `/createaccount`", ephemeral=True)
            return

        self.db.cur.execute("SELECT * FROM active_loans WHERE debtor_id = ? AND lender_id = ? AND status = 'pending'", (debtor_id, lender_id))
        existing_loan = self.db.cur.fetchone()

        if existing_loan:
            await interaction.response.send_message(f"{interaction.user.mention}, you already have a pending loan request from {user.mention}.", ephemeral=True)
            return

        self.db.cur.execute("SELECT wallet FROM economy WHERE user_id = ?", (lender_id,))
        lender_balance = self.db.cur.fetchone()[0]

        if not self.check_balance(lender_balance, amount):
            await interaction.response.send_message(f"Sorry, but {user.mention} doesn't have enough balance to lend {amount} :)'s.", ephemeral=True)
            return

        await interaction.response.send_message(f"{user.mention}, {interaction.user.mention} is requesting a loan of {amount} :)'s. Do you accept? (yes/no)")

        def check(message: Message):
            return message.author == user and message.channel == interaction.channel

        try:
            response = await self.bot.wait_for("message", timeout=30.0, check=check)
            if response.content.lower() == "yes":
                self.db.cur.execute("""
                    INSERT INTO active_loans (debtor_id, lender_id, amount, status)
                    VALUES (?, ?, ?, 'pending')
                """, (debtor_id, lender_id, amount))

                self.db.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (amount, debtor_id))
                self.db.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (amount, lender_id))
                self.db.db.commit()

                await interaction.followup.send(f"{user.mention}, you've successfully lent {amount} :)'s to {interaction.user.mention}.")
            else:
                await interaction.followup.send(f"{user.mention}, you've declined {interaction.user.mention}'s loan request.")
        except TimeoutError:
            await interaction.followup.send("Loan request timed out.")

    @app_commands.command(name="repay", description="Repay your active loan to a specific user")
    async def repay(self, interaction: Interaction, amount: int, recipient: Member):
        user_id = interaction.user.id

        account = await self.check_account(user_id)
        if not account:
            return await interaction.response.send_message("Account not found, please create one using `/createaccount`", ephemeral=True)

        self.db.cur.execute("SELECT wallet FROM economy WHERE user_id = ?", (user_id,))
        wallet_balance = self.db.cur.fetchone()[0]
        
        loan = self.db.get_active_loan(user_id)
        if not loan:
            raise NoActiveLoan()

        loan_id, loan_amount = loan

        if not await self.check_balance(user_id, amount):
            raise InsufficientFunds(wallet_balance, amount)

        if amount > loan_amount:
            return await interaction.response.send_message(f"You are trying to repay more than the outstanding loan balance of {loan_amount}.", ephemeral=True)

        try:
            self.db.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (amount, user_id))
            self.db.repay_loan(loan_id, amount)

            if amount == loan_amount:
                self.db.mark_loan_repaid(loan_id)

            self.db.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (amount, recipient.id))

            await interaction.response.send_message(f"Successfully repaid {amount} from your loan to {recipient.name}. Remaining loan balance: {loan_amount - amount}.")
        
        except Exception as e:
            await interaction.response.send_message(f"An error occurred while processing your repayment: {str(e)}", ephemeral=True)

    """
    Shop
    """

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
    
    async def show_shop(self, interaction: Interaction, page: int = 0):
        items = self.shop_items()
        start = page * self.items_per_page
        end = start + self.items_per_page
        shop_page = items[start:end]

        embed = Embed(title="Shop Items", description="", color=Color.random())
        for item in shop_page:
            embed.add_field(name=item[0], value=f"Price: {item[1]} :)'s", inline=False)
        
        view = ui.View()

        if page > 0:
            prev_button = ui.Button(label="Previous", style=ButtonStyle.primary)
            prev_button.callback = lambda _: self.show_shop(interaction, page - 1)
            view.add_item(prev_button)

        if end < len(items):
            next_button = ui.Button(label="Next", style=ButtonStyle.primary)
            next_button.callback = lambda _: self.show_shop(interaction, page + 1)
            view.add_item(next_button)
        
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="shop", description="Browse the shop items")
    async def shop(self, interaction: Interaction):
        await self.show_shop(interaction)

    @app_commands.command(name="buy", description="Buy an item from the shop")
    async def buy(self, interaction: Interaction, item_name: str, quantity: int):
        user_id = interaction.user.id
        account = self.check_account(user_id)

        if not account:
            await interaction.response.send_message("You don't have an active account. Please create one using the 'create_account' command.", ephemeral=True)
            return
        
        items = self.shop_items()
        item = next((i for i in items if i[0].lower() == item_name.lower()), None)

        if not item:
            await interaction.response.send_message("Invalid item name. Please check the spelling and try again.", ephemeral=True)
            return
        
        _item_name, price = item
        total_cost = price * quantity

        self.db.cur.execute("SELECT wallet FROM economy WHERE user_id = ?", (user_id,))
        wallet_balance = self.db.cur.fetchone()[0]

        if self.check_balance(wallet_balance, total_cost):
            self.db.cur.execute(
                "INSERT INTO user_assets (user_id, item_id, quantity) VALUES (? ,?, ?) ON CONFLICT(user_id, item_id) DO UPDATE SET quantity = quantity + ?",
                (user_id, item[0], quantity, quantity,)
            )
            self.db.cur.execute("UPDATE economy SET wallet = wallet - ? WHERE user_id = ?", (total_cost, user_id,))
            self.db.db.commit()

            await interaction.response.send_message(f"Successfully bought {quantity}x {_item_name} for {total_cost} :)'s. Your new balance is {wallet_balance - total_cost}.", ephemeral=False)
        else:
            await interaction.response.send_message("Insufficient funds. Please check your wallet balance and try again.", ephemeral=True)

    @app_commands.command(name="sell", description="Sell an item from your assets")
    async def sell(self, interaction: Interaction, item_name: str, quantity: int):
        user_id = interaction.user.id
        account = self.check_account(user_id)

        if not account:
            await interaction.response.send_message("You don't have an active account. Please create one using the 'create_account' command.", ephemeral=True)
            return
        
        items = self.shop_items()
        item = next((i for i in items if i[0].lower() == item_name.lower()), None)

        if not item:
            await interaction.response.send_message("Invalid item name. Please check the spelling and try again.", ephemeral=True)
            return
        
        _item_name, price = item
        
        self.db.cur.execute("SELECT quantity FROM user_assets WHERE user_id = ? AND item_id = ?", (user_id, item_name))
        result = self.db.cur.fetchone()

        if not result or result[0] < quantity:
            await interaction.response.send_message("You don't have enough of that item to sell. Please check your inventory and try again.", ephemeral=True)
            return
        
        self.db.cur.execute("UPDATE user_assets SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?", (quantity, user_id, item_name))
        self.db.cur.execute("UPDATE economy SET wallet = wallet + ? WHERE user_id = ?", (quantity * price, user_id))
        self.db.db.commit()

        await interaction.response.send_message(f"Successfully sold {quantity}x {_item_name} for {quantity * price} :)'s. Your new balance is {self.check_balance(account['wallet'], quantity * price)}.", ephemeral=False)

    @app_commands.command(name="assets", description="View your assets")
    async def assets(self, interaction: Interaction):
        user_id = interaction.user.id
        account = self.check_account(user_id)

        if not account:
            await interaction.response.send_message("You don't have an active account. Please create one using the 'create_account' command.", ephemeral=True)
            return
        
        self.db.cur.execute("SELECT item_name, quantity FROM user_assets WHERE user_id = ?", (user_id,))
        assets = self.db.cur.fetchall()

        if not assets:
            await interaction.response.send_message("You don't have any assets.", ephemeral=True)
            return
        
        embed = Embed(title="Your Assets", description="", color=Color.random())
        for name, quantity in assets:
            embed.add_field(name=name, value=f"Quantity: {quantity}", inline=False)

        await interaction.response.send_message(embed=embed)

    # TODO:

    """
    Earning Money
    """

    # /work - Work to earn a random amount of money.
    # /job - Check your current job and salary.
    # /apply <job> - Apply for a specific job (e.g., waiter, programmer).
    # /startbusiness <business_name> - Start a business for passive income.
    # /sell <item> - Sell an item for a specified amount.
    # /hustle - Take a risk to earn more money.
    # /gamble <amount> - Gamble money in a game of chance.

    """
    Investments
    """

    # /invest <amount> - Invest money in stocks or cryptocurrency.
    # /portfolio - Check your investment portfolio.
    # /dividends - Collect dividends from your investments.
    # /sell_stock <stock> - Sell a specific stock.
    # /market - View current market trends and prices.
    # /buy_stock <stock> <amount> - Buy a specified amount of stock.
    # /crypto - View current cryptocurrency prices.

    """
    Aunctions and Marketplaces
    """

    # /auction <item> <price> - Start an auction for an item.
    # /bid <auction_id> <amount> - Place a bid on an auction.
    # /end_auction <auction_id> - End a specified auction.
    # /marketplace - View the marketplace for items.
    # /list_item <item> - List an item for sale in the marketplace.

    """
    Miscellaneous
    """

    # /mine - Mine for resources to sell.
    # /farm - Farm for produce to sell.
    # /hunt - Hunt for animals and sell meat.
    # /forage - Forage for items in the wild.
    # /quests - View available quests for earning money.
    # /complete_quest <quest_id> - Complete a specific quest for rewards.
    # /leaderboard - View the economy leaderboard.
    # /store - Access the virtual store for special items.
    # /loyalty - Check your loyalty points for rewards.

    """
    Miscellaneous Actions
    """

    # /tax - View the current tax rate and your tax obligations.
    # /settax <amount> set the tax amount for the server (done by admin)
    # /taketax take tax from everyone in the database and add it to the users bank (done by admin)
    # /donate <amount> - Donate money to a charity or server fund.
    # /steal <user> - Attempt to steal money from another user.
    # /rob <user> - Rob another user (with a chance of failure).
    # /bounty <user> - Place a bounty on another user.

    """
    Economy Tips
    """

    # /tips - Get tips for managing your economy.
    # /faq - Frequently asked questions about the economy system.
    # /guide - Access a guide on how to earn money.

    """
    Error Handling
    """

    @repay.error
    async def repay_error(self, interaction: Interaction, error: Exception):
        if isinstance(error, NoActiveLoan):
            await interaction.response.send_message(error.message, ephemeral=True)
        elif isinstance(error, InsufficientFunds):
            await interaction.response.send_message(error.message, ephemeral=True)
        else:
            await interaction.response.send_message("An error occurred while trying to repay your loan. Please try again later.", ephemeral=True)

    def cog_unload(self):
        self.db.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))