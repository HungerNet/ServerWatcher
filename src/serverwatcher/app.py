from calagoapi.extensions import enable
from .connection import setupServer

enable('minecraft') # enables calagoapi-minecraft



def main():
    # setup server (panel.connect)
    panel, server = setupServer()

    # setup router

    # log "successful connection"

    # take snapshot

    # evaluate action based on target values

    # perform action (if any)

    # wait for confirmation that action was successful

    # disconnect from panel (panel.disconnect)

    # sleep for configured time

    # loop to beginning
