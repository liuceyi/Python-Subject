import asyncio
import danmaku


async def printer(q):
    while True:
        m = await q.get()
        print(m)
        if m['msg_type'] == 'danmaku':
            print(f'{m["name"]}：{m["content"]}')


async def main(url):
    q = asyncio.Queue()
    dmc = danmaku.DanmakuClient(url, q)
    asyncio.create_task(printer(q))
    await dmc.start()


a = input('请输入直播间地址：\n')
asyncio.run(main(a))