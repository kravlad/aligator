from defs import send_telegram
import asyncio




text = 'cbr.ru / yahoo.com | #финансы\n\n<pre>Индексы</pre>:\n<a href="https://www.moex.com/ru/index/IMOEX">🔴</a><pre>ММВБ 2 222.51 (-0.19%)</pre>\n🟢<a href="https://www.moex.com/ru/index/RTSI">РТС</a> 1 144.79 (1.09%)\n\ncbr.ru / yahoo.com | #финансы'

asyncio.run(send_telegram(text))