import asyncio

async def tcp_echo_client():
    inter = 0
    shake = 0
    reader, writer = await asyncio.open_connection(
        '115.196.131.122',16881)

    #print(f'Send: {message!r}')
    writer.write(b'\x13BitTorrent protocol00000000_\xff\x0e\x1c\x8a\xc4\x14\x86\x03\x10\xbc\xc1\xcbv\xac(\xe9`\xef\xbeqwertyuiopasdfghjklz')
    data = await reader.read(2000)
    print(f'first Received: {data!r}')

    data1 = await reader.read(2000)

    print(f'second Received: {data1!r}')
    writer.write(b'\x00\x00\x00\x01\x02')
    data3 = await reader.read(2000)

    print(f'third Received: {data3!r}') 
    writer.write(b'\x00\x00\x00\r\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00@\x00')
    data4 = await reader.read(17000)
    print(f'forth Received: {data4!r}')

    writer.write(b'\x00\x00\x00\x01\x02')

    writer.write(b'\x00\x00\x00\r\x06\x00\x00\x00\x00\x00\x00@\x00\x00\x00\x80\x00')
    data5 = await reader.read(17000)
    print(f'fifth Received: {data5!r}')
    print(len(data4))
    print(len(data5))

    data6 = await reader.read(17000)
    print(f'fifth Received: {data6!r}')
    print(len(data4))
    print(len(data5))
    print(len(data6))
    print('Close the connection')
    writer.close()

loop =asyncio.get_event_loop()
#task = asyncio.create_task(tcp_echo_client())
loop.run_until_complete(tcp_echo_client())