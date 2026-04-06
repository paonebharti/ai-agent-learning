import asyncio

async def slow_task():
    await asyncio.sleep(2)
    return "done"

async def main():
    print("start")
    result = await slow_task()
    print(result)

asyncio.run(main())
