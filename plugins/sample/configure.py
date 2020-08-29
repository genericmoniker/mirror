"""Configuration module for the plugin.

This module gets called to help the user set any desired configuration for the plugin.
It can store configuration data in the supplied database for later retrieval in the
Flask blueprint for the plugin.
"""

def configure_plugin(db):
    name = input("What is your name?")
    db["recipient"] = name or 'world'
