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

def get_value(obj, key, default=None):
    try:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)
    except Exception:
            return default

@register("groupGuard", "wuyufeng9960", "防重复加群", "0.9.0")
class MyPlugin(Star):

    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.monitor_groups = [str(g) for g in config.get("monitor_groups", []) or []]
        self.detect_groups = [str(g) for g in config.get("target_groups", []) or []]
        self.alert_groups = config.get("alert_groups")

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
            try:
                for target_group in self.detect_groups:
                    try:
                        logger.debug(f"检查用户 {user_id} 是否在目标群 {target_group} 中")
                        # 使用 get_group_member_list 获取群成员列表，并在返回的成员中匹配 user_id 或 group_user_id
                        resp = await client.api.call_action('get_group_member_list', group_id=int(target_group), no_cache=False)
                        members = None
                        if isinstance(resp, dict):
                            members = resp.get('data') or resp.get('members')
                        else:
                            members = resp

                        if members:
                            for m in members:
                                gid_user_id = get_value(m, 'group_user_id', None) or get_value(m, 'user_id', None)
                                if gid_user_id is None:
                                    continue
                                
                                # 比较 user_id 和 gid_user_id
                                try:
                                    if int(gid_user_id) == int(user_id):
                                        
                                        logger.info(f"用户 {user_id} 已在目标群 {target_group} 中，将拒绝加群申请")
                                        
                                        try:
                                            await client.api.call_action('set_group_add_request', flag=get_value(raw_message, 'flag'), approve=False, reason=f"您已在群 {target_group} 中，请不要重复加群。")
                                        except Exception as e:
                                            logger.error(f"拒绝用户 {user_id} 加群申请时出错，详情请查询日志")
                                            if self.alert_groups:
                                                await client.api.call_action('send_group_msg', group_id=int(self.alert_groups), message=f"拒绝用户 {user_id} 加群申请时出错: {e}")
                                        
                                        # 发送提示信息到指定群
                                        if self.alert_groups:
                                            try:
                                                await client.api.call_action('send_group_msg', group_id=int(self.alert_groups), message=f"用户 {user_id} 已在群 {target_group} 中，拒绝加群申请。")
                                            except Exception as e:
                                                logger.warn(f"发送提示信息到群 {self.alert_groups} 时出错: {e}")
                                        
                                        # 结束检查
                                        return None

                                # 处理比较时的异常
                                except Exception as e:
                                    logger.error(f"比较用户 ID 时出错: {e}")
                                
                    except Exception as e:
                        yield event.plain_result(f"检查用户 {user_id} 在群 {target_group} 中时出错，具体信息请查阅日志", to_groups=self.alert_groups)
                        logger.warn(f"检查用户 {user_id} 在群 {target_group} 中时出错: {e}") 
                
                logger.info(f"用户 {user_id} 不在任何目标群中，将跳过处理")
            
            except Exception as e:
                logger.error(f"处理加群申请时出错: {e}\n{traceback.format_exc()}")
        
        return None