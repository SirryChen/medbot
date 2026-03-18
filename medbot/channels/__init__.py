"""Chat channels module with plugin architecture."""

from medbot.channels.base import BaseChannel
from medbot.channels.manager import ChannelManager

__all__ = ["BaseChannel", "ChannelManager"]
