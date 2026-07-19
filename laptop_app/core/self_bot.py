"""Compliant Discord bot gateway monitor.
Uses an application bot token, never a Discord user token. It reads only the configured channel and
never sends messages, reactions, commands, or API mutations.
"""
import asyncio, logging, threading
from PyQt6.QtCore import QObject, pyqtSignal
class DiscordMonitor(QObject):
    state_changed=pyqtSignal(str); raid_detected=pyqtSignal(dict); error=pyqtSignal(str)
    def __init__(self, config): super().__init__(); self.config=config; self._thread=None; self._stop=False; self.client=None
    def start(self):
        if self._thread and self._thread.is_alive(): return
        self._stop=False; self._thread=threading.Thread(target=self._run,daemon=True,name='DiscordMonitor'); self._thread.start()
    def stop(self):
        self._stop=True
        if self.client:
            try: asyncio.run_coroutine_threadsafe(self.client.close(),self.client.loop)
            except Exception: pass
    def _run(self):
        try:
            import discord
            token=self.config['discord']['bot_token']; channel_id=int(self.config['discord']['channel_id'])
            if not token or not channel_id: raise ValueError('Set an application bot token and channel ID first.')
            intents=discord.Intents.none(); intents.guilds=True; intents.messages=True; intents.message_content=True
            monitor=self
            class Client(discord.Client):
                async def on_ready(self): monitor.state_changed.emit('connected')
                async def on_disconnect(self): monitor.state_changed.emit('disconnected')
                async def on_message(self,message):
                    if message.channel.id != channel_id or message.author.bot: return
                    target=monitor.config['discord'].get('user_id','').strip()
                    mentioned=not target or any(str(u.id)==target for u in message.mentions) or target in message.content
                    if mentioned: monitor.raid_detected.emit({'author':str(message.author),'content':message.content,'channel_name':getattr(message.channel,'name',str(channel_id))})
            self.client=Client(intents=intents); self.state_changed.emit('connecting'); self.client.run(token,log_handler=logging.getLogger('discord'))
        except Exception as exc: logging.getLogger(__name__).exception('Discord monitor failed'); self.error.emit(str(exc)); self.state_changed.emit('disconnected')
    @staticmethod
    def test_token(token):
        """Token validation is intentionally handled by a live connection, not a token scraping endpoint."""
        return bool(token and token.startswith(('Bot ','MT','OD')))
