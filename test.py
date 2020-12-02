import asyncio

async def tcp_echo_client():
    reader, writer = await asyncio.open_connection(
        '79.56.135.89',51413)

    #print(f'Send: {message!r}')
    writer.write(b'\x13BitTorrent protocol00000000_\xff\x0e\x1c\x8a\xc4\x14\x86\x03\x10\xbc\xc1\xcbv\xac(\xe9`\xef\xbe-TR2940-k11ga2y21h22')

    data = await reader.read(100)
    print(f'Received: {data!r}')

    print('Close the connection')
    writer.close()

asyncio.run(tcp_echo_client())