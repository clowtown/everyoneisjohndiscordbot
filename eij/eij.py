import discord
from discord.ext import commands
import random

class EiJ:
    """My Everyone Is John cog!"""
    
    def __init__(self, bot):
        self.bot = bot
        self.bids={}
        self.server_last_winner = {}

    @commands.command()
    async def john(self):
        await self.bot.say("oh, hi - wait?! Who's this?")

    @commands.command()
    async def newgame(self, channel : discord.Channel):
        """ start new eij game """
        await self.bot.change_presence(game=discord.Game(name='Everyone Is John | #help'))
        bank = self.bot.get_cog('Economy').bank
        resp = [] 
        bank.wipe_bank(channel.server)
        resp.append("server bank wiped")
        for user in channel.server.members:
            self.bids[user] = 0 
            if not user.bot and user.status == discord.Status.online:
                user.game=discord.Game(name='Everyone Is John')
                if not bank.account_exists(user):
                    bank.create_account(user)
                bank.set_credits(user,10)
                resp.append("[{},{},balance:{}]".format(user , user.status , bank.get_balance(user)))
        await self.bot.say("Channel:{} \n".format(channel) + '\n'.join(resp))
    
    @commands.command(pass_context=True,no_pm=False)
    async def bid(self,ctx,bid : int):
        """ user bid via PM """
        self.bids[ctx.message.member] = bid
        bank = self.bot.get_cog('Economy').bank
        if not bank.account_exists(ctx.message.member):
            await self.bot.say("you aren't in a game")
        elif bank.get_balance(ctx.message.author) < bid:
            await self.bot.say("you're cheating{}<{}".format(bank.get_balance(ctx.message.author),bid))
        else: await self.bot.say("{} bid {}".format(ctx.message.author,bid))

    @commands.command(pass_context=True)
    async def start(self,ctx):
        """ Bid for Control """
        bank = self.bot.get_cog('Economy').bank
        resp=[]
        for user in ctx.message.server.members:
            self.bids[user] = 0 
            if not user.bot and user.status == discord.Status.online:
                if not bank.account_exists(user):
                    bank.create_account(user)
                bank.deposit_credits(user,1)
                resp.append("{}:{}".format(user,bank.get_balance(user)))
        await self.bot.say("1..2..3..bid for control!\n{}".format("\n".join(resp)))

    @commands.command(pass_context=True)
    async def end(self,ctx):
        """ End Bid for Control """
        bank = self.bot.get_cog('Economy').bank
        winner = [] #future use last user
        if not self.server_last_winner.get(ctx.message.server,None) == None:
            winner.append(self.server_last_winner[ctx.message.server])
        winBid = 0
        resp = []
        for user in ctx.message.server.members:
            value  = self.bids[user]
            if bank.can_spend(key,value): 
                if value > winBid:
                    winner = [] 
                    winner.append(key) 
                    winBid = int(value)
                elif value == winBid:
                    winner.append(key) 
            else:
                resp.append("{} tried to cheat".format(key))
        if len(winner) > 0:
            if len(winner) > 1:
                resp.append("Roll Off bid of {} between {}".format(winBid,"/".join(winner)))
            else:
                bank.withdraw_credits(winner[0],winBid)
                self.server_last_winner[ctx.message.server]=winner[0]
                await self.bot.say("{}\n{} wins the bid for control with a {}!".format("\n".join(resp),str(winner),winBid))
        else:
            await self.bot.say("{}\n Pussies..no change in control".format("\n".join(resp)))

def setup(bot):
    bot.add_cog(EiJ(bot))

