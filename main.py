import asyncio
import time
import traceback
import json
from pathlib import Path
from typing import List, Dict
import aiohttp
import os
import shutil

from astrbot.api import logger
from astrbot.api.star import StarTools
from astrbot.api import message_components as Comp
from astrbot.api.star import Context, Star, register
from astrbot.core.message.message_event_result import MessageChain
from astrbot.api.platform import MessageType
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.core.star.filter.platform_adapter_type import PlatformAdapterType

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.monitor_groups = [str(g) for g in config.get("monitor_groups", []) or []]
        self.detect_groups = [str(g) for g in config.get("target_groups", []) or []]


    def get_value(obj, key, default=None):
        try:
            if isinstance(obj, dict):
                return obj.get(key, default)
            return getattr(obj, key, default)
        except Exception:
            return default


    @filter.platform_adapter_type(PlatformAdapterType.AIOCQHTTP)
    @filter.event_message_type(filter.EventMessageType.ALL, priority=10)
    async def groupin(self, event: AstrMessageEvent):
        """处理加群申请"""
        raw_message = event.message_obj.raw_message
        post_type = get_value(raw_message, "post_type")
        if post_type == "request" and get_value(raw_message, "request_type") == "group":
            group_id = get_value(raw_message, "group_id")
            user_id = get_value(raw_message, "user_id")
            if str(group_id) not in self.monitor_groups: return None
            logger.debug(f"收到用户 {user_id} 加群 {group_id} 的申请, 开始检查是否允许通过")
            # 检查申请人是否在目标群中
            client = event.bot
            for target_group in self.detect_groups:
                member_status = await client.api.call_action('get_group_member_info', group_id=int(target_group), user_id=int(user_id))
                retcode = member_status.get('retcode', retcode)
                if retcode == 0:
                    logger.info(f"用户 {user_id} 已在目标群 {target_group} 中，将拒绝加群申请")
                    await client.api.call_action('set_group_add_request', flag=get_value(raw_message, 'flag'), sub_type='add', approve=False, reason=f"您已在群 {target_group} 中，请不要重复加群。")
                    return None
            logger.info(f"用户 {user_id} 不在任何目标群中，将跳过处理")