from random import randint

"""Base Command"""

class Command:
    name = "Command"
    desc = "Base command."
    keyword = ""
    passed_input = []

    def __init__(self, passed_input):
        self.passed_input = passed_input

    async def fire(self):
        return

"""Specific commands"""

class OutputText(Command):
    name = "Output text"
    desc = "Outputs text from the bot to the channel"
    keyword = "output"

    async def fire(self):
        output = " ".join(self.passed_input)
        return output

class RollDice(Command):
    name = "Dice roll"
    desc = "Outputs the result of a dice roll to the channel."
    keyword = "dice"
    num_dice = 0
    dice_value = 0

    def __init__(self, num, value):
        self.num_dice = num
        self.dice_value = value

    def fire(self):
        dice = []
        total = 0
        while self.num_dice > 0:
            roll = randint(1, self.dice_value)
            dice.append(str(roll))
            total = total + roll
            self.num_dice = self.num_dice - 1

        output = "**Dice Rolled**\n"
        output += ", ".join(dice)
        output += "\nTotal: {0}".format(total)
        return output




def diceroll(num, sides):
    total = 0
    for dice in range(num):
        total += randint(1, sides)
    return total