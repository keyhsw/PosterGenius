from http import HTTPStatus
import random
import re
import gradio as gr
from core.client import GeneratePoster, GeneratePromptQwen

from core.const import TextLength


def generate_text(title):
    if len(title) == 0:
        raise gr.Error("请输入标题，或者点击下面的样例自动填充输入参数")
        
    chat = GeneratePromptQwen()
    response = chat.generate_chat(f'以{title}为主题，生成{TextLength.title}个字以内的标题，{TextLength.subtitle}个字以内副标题，以及生成{TextLength.body}个字以内的正文')
    texts = re.findall('：(.*)\n', response + '\n')
    title = texts[0][:TextLength.title]
    subtitle = texts[1][:TextLength.subtitle]
    content = texts[2][:TextLength.body].split('。')[0]
    return subtitle, content



def process_poster_generation(args):
    genetor = GeneratePoster()
    img_lists = genetor.request(args)
    return img_lists