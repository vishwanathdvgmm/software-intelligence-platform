import asyncio
import qdrant_client
import json

async def run() -> None:
    c = qdrant_client.AsyncQdrantClient('http://localhost:6333')
    cnt = await c.count('sip_knowledge')
    print('TOTAL:', cnt)
    res = await c.scroll(collection_name='sip_knowledge', limit=1)
    if res and res[0]:
        print('SAMPLE PAYLOAD:', json.dumps(res[0][0].payload, indent=2))
    else:
        print('NO RESULTS IN SCROLL')

asyncio.run(run())
