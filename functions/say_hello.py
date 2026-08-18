from datetime import timedelta

import inngest

from inngest_client import inngest_client


@inngest_client.create_function(
    fn_id="say-hello",
    trigger=inngest.TriggerEvent(event="test/hello"),
)
async def say_hello(ctx: inngest.Context) -> str:
    await ctx.step.sleep("wait-a-bit", timedelta(seconds=5))
    return "Hello from the background!"
