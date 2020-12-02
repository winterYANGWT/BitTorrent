import asyncio

async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        '179.192.71.213',51413)

    #print(f'Send: {message!r}')
    writer.write(b'\x13BitTorrent protocol000000005fff0e1c8ac414860310bcc1cb76ac28e960efbe-TR3000-m4vdyu2yzpzn')

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()

asyncio.run(tcp_echo_client())