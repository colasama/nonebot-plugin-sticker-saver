from nonebot.plugin import on_command, PluginMetadata
from nonebot import on_message, logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from httpx import AsyncClient

__plugin_meta__ = PluginMetadata(
    name="表情包保存器",
    description="一款很简单的，用于保存已经不提供保存选项的 QQ 表情包的 Nonebot 插件",
    usage="以 .save 命令回复表情包即可.\n机器人回复的静态表情可以直接保存，动态表情可以通过短链接保存。",
    type="application",
    homepage="https://github.com/colasama/nonebot-plugin-sticker-saver",
    supported_adapters={"~onebot.v11"}
)

face_extractor = on_command('save', aliases={'保存图片', '保存表情', '保存'}, priority=10, block=True)

@face_extractor.handle()
async def handle_face_extraction(bot: Bot, event: MessageEvent):
    if event.reply:
        # 获取被回复的消息内容
        original_message = event.reply.message
        # 提取表情包并发送回去，静态表情包可以直接被保存
        for seg in original_message:
            logger.debug("seg: " + seg + " type: " + str(seg.type))
            if seg.type == "image":
                content = MessageSegment.text("表情：") + MessageSegment.image(seg.data["url"], type_=0)
                async with AsyncClient() as client:
                    # 用于 .gif 格式的表情包保存，加上一层短链接防止可能的检测，可以修改不同的 API
                    url = "https://t.apii.cn/?url=" + str(seg.data["url"])
                    try:
                        req = await client.get(url=url)
                        result = req.json()
                        data = result.get("url")
                    except Exception as e:
                        await bot.send(event, "获取短链接失败")
                await bot.send(event, content + "原始链接：" + data)
                return
        await bot.send(event, "未在回复内容中检测到表情...")
    # 如果没有回复消息
    else:
        await bot.send(event, "只有回复表情才可以用捏")