import sqlite3
import time
from discord.ext import commands

class Modlog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = sqlite3.connect("utils/database/modlog.db")
        self.cur = self.db.cursor()
        self.setup_db()

    def setup_db(self):
        """Initializes the database table for mod logging."""
        self.cur.execute("""        
            CREATE TABLE IF NOT EXISTS modlog (
                user_id INTEGER,
                action TEXT,
                reason TEXT,
                timestamp INTEGER,
                moderator_id INTEGER,
                warning_id INTEGER
            )             
        """)
        self.db.commit()

    def log_action(self, user_id: int, action: str, reason: str, moderator_id: int, warning_id: str):
        """Logs an action taken on a member."""
        timestamp = int(time.time())
        self.cur.execute(
            """INSERT INTO modlog (user_id, action, reason, timestamp, moderator_id, warning_id) VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, action, reason, timestamp, moderator_id, warning_id)
        )
        self.db.commit()

    def clear_logs_for_member(self, member_id: int):
        """Clears all mod logs related to a specific member."""
        try:
            self.cur.execute("DELETE FROM modlog WHERE user_id = ?", (member_id,))
            self.db.commit()
        except sqlite3.Error as e:
            print(f"Error clearing logs for member {member_id}: {str(e)}")

    def delete_log_by_warning_id(self, warn_id: str):
        """Deletes a specific log entry based on the warning ID."""
        try:
            self.cur.execute("DELETE FROM modlog WHERE warning_id = ?", (warn_id,))
            self.db.commit()
        except sqlite3.Error as e:
            print(f"Error deleting log entry with warning ID {warn_id}: {str(e)}")

    def cog_unload(self):
        """Closes the database connection when the cog is unloaded."""
        self.db.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Modlog(bot))