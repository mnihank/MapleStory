from PIL import Image
from googletrans import Translator
import asyncio

class translate():

    def __init__(self):
        pass
    def setup(self):
    # setting
        self.img = Image.open('test.png')
        self.translator = Translator()
    async def run(self, text=""):
        # translate action
        result = await Translator().translate(text, src="en", dest="zh-tw")
        print(result.text)
        return result.text

if __name__ == "__main__":
    app = translate()
    app.setup()
    asyncio.run(app.run())