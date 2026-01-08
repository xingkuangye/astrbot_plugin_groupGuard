# astrbot_plugin_groupGuard

![License](https://img.shields.io/badge/license-GPL--3.0-green)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![AstrBot](https://img.shields.io/badge/framework-AstrBot-blue)

**本插件仅支持 napcat**

## 功能描述

**groupGuard** 是一个 Astrbot 插件，用于防止成员申请加入多个同系列群

## ⚙️ 配置说明

| 配置项                              | 类型          | 默认值  | 描述                                                         |
| :---------------------------------- | :------------ | :------ | :----------------------------------------------------------- |
| **`monitor_groups`**        | `list[str]` | `[]`  | 要监控入群事件的群号列表。                                   |
| **`target_groups`**      | `list[str]` | `[]`  | 匹配群成员的**群号**  |
| **`alert_group`**         | `int` | `123456`  | 用于接收日志的**群号**（可不填） |

## ❤️支持

* [AstrBot 帮助文档](https://astrbot.app)
* 如果您在使用中遇到问题，欢迎在本仓库提交 [Issue](https://github.com/xingkuangye/astrbot_plugin_groupGuard/issues)