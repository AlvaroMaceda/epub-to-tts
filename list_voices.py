from edge_tts import VoicesManager
import asyncio

async def get_voices():
    voices = await VoicesManager.create()
    en_voices = [v for v in voices.voices if v['Locale'].startswith('en')]
    es_voices = [v for v in voices.voices if v['Locale'].startswith('es')]

    print('English voices:')
    for v in en_voices:
        print(f"{v['ShortName']}: {v.get('DisplayName', '')} ({v['Locale']})")

    print('\nSpanish voices:')
    for v in es_voices:
        print(f"{v['ShortName']}: {v.get('DisplayName', '')} ({v['Locale']})")

if __name__ == "__main__":
    asyncio.run(get_voices())
