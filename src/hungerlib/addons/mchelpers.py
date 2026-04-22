# Minecraft-specific helper functions that operate on a MinecraftServer instance.

class MCHelpers:
    def __init__(self, server):
        """
        Helper utilities for a MinecraftServer instance.
        """
        self.server = server

    def run(self, command):
        """Send a raw RCON command."""
        return self.server._rcon_send(command)

    def tellraw(self, target, message):
        """Send a tellraw message with color translation."""
        translated = self.server._translate_mc_colors(message)
        safe = translated.replace('"', '\\"')
        cmd = f'tellraw {target} {{"text":"{safe}"}}'
        return self.run(cmd)

    def kick(self, player, message="Kicked"):
        safe = message.replace('"', '\\"')
        return self.run(f'kick {player} "{safe}"')

    def kickAll(self, message="Server restarting"):
        safe = message.replace('"', '\\"')
        return self.run(f'kick @a "{safe}"')

    def whitelistAdd(self, player):
        return self.run(f"whitelist add {player}")

    def whitelistRemove(self, player):
        return self.run(f"whitelist remove {player}")

    def whitelistList(self):
        return self.run("whitelist list")

    def runFunction(self, function_name):
        """Run a datapack function."""
        return self.run(f"function {function_name}")

    def enableDatapack(self, name):
        return self.run(f"datapack enable {name}")

    def disableDatapack(self, name):
        return self.run(f"datapack disable {name}")

    def listDatapacks(self):
        return self.run("datapack list")

    # ============================================================
    # GAMERULE HELPERS
    # ============================================================

    def setGamerule(self, rule, value):
        return self.run(f"gamerule {rule} {value}")

    def getGamerule(self, rule):
        return self.run(f"gamerule {rule}")

    # ============================================================
    # SCOREBOARD HELPERS
    # ============================================================

    def scoreboardAddObjective(self, name, criteria="dummy", display_name=None):
        if display_name:
            safe = display_name.replace('"', '\\"')
            return self.run(f'scoreboard objectives add {name} {criteria} "{safe}"')
        return self.run(f"scoreboard objectives add {name} {criteria}")

    def scoreboardRemoveObjective(self, name):
        return self.run(f"scoreboard objectives remove {name}")

    def scoreboardSetDisplay(self, slot, objective):
        return self.run(f"scoreboard objectives setdisplay {slot} {objective}")

    def scoreboardSet(self, player, objective, value):
        return self.run(f"scoreboard players set {player} {objective} {value}")

    def scoreboardAdd(self, player, objective, value):
        return self.run(f"scoreboard players add {player} {objective} {value}")

    def scoreboardGet(self, player, objective):
        return self.run(f"scoreboard players get {player} {objective}")

    # ============================================================
    # TIME & WEATHER HELPERS
    # ============================================================

    def setTime(self, value):
        return self.run(f"time set {value}")

    def addTime(self, value):
        return self.run(f"time add {value}")

    def setWeather(self, weather, duration=None):
        if duration:
            return self.run(f"weather {weather} {duration}")
        return self.run(f"weather {weather}")

    # ============================================================
    # BROADCAST HELPERS
    # ============================================================

    def broadcast(self, message):
        """Broadcast using tellraw @a."""
        return self.tellraw("@a", message)
