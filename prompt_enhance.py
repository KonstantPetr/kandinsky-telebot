import os
from dotenv import find_dotenv, load_dotenv
from huggingface_hub import InferenceClient
from extentions import text_shop, random_temperature


class Text2TextAPI:
    def __init__(self, api_key, model, timeout=5):
        self.client = InferenceClient(token=api_key, timeout=timeout, model=model)

    def generate(self, prompt, max_new_tokens=100, temperature=0.5, seed=None, attempts=10):
        while attempts > 0:
            try:
                temperature = random_temperature()
                output = self.client.text_generation(
                    prompt=f'{text_shop["prompt_helper_t2t"][0]}{prompt}{text_shop["prompt_helper_t2t"][1]}',
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    seed=seed)
                output = output.strip('\n').split('Промпт:')[1].strip('\n').strip()
                if 'конец' in output.lower():
                    output = output.split(':конец')[0].strip()
                return output
            except Exception:
                attempts -= 1
                continue
        return prompt


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    HF_KEY = os.environ.get('HF_KEY')
    text_gen = Text2TextAPI(HF_KEY, text_shop['model_t2t'])
    print(text_gen.generate('жуткий монстр в стиле Лавкрафта'))
