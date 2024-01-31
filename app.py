import random
from concurrent.futures import ProcessPoolExecutor, as_completed
import json, cv2, requests, base64
import uuid
import time
import socket
import numpy as np
import os, sys, copy

from core.const import TextLength
from core.core import generate_text, process_poster_generation

sys.path.insert(0, './')

import os.path as osp
import numpy as np
import gradio as gr
import json
# vis all box
from PIL import Image, ImageDraw
from core.log import logger

import uuid, time

results_cache_dir = "results_cache"
examples_dir = ['example/春节', 'example/2D极简',  'example/3D卡通','example/刺绣风','example/水墨风','example/折纸工艺','example/pick1']
random.seed(100)

def shuffle_examples(examples_dir_idx=0):
    ## samples0
    samples1 = []
    for ff in os.listdir(examples_dir[examples_dir_idx]):
        if ff.endswith(".jpeg"):
            samples1.append(ff)
    random.shuffle(samples1)
    return samples1


def generate(title, sub_title, body_text, prompt_text_zh, prompt_text_en, text_template):
    if len(title) > TextLength.title:
        raise gr.Error(f"主标题最多支持{TextLength.title}个字符")
        return
    if len(sub_title) > TextLength.subtitle:
        raise gr.Error(f"主标题最多支持{TextLength.subtitle}个字符")
        return

    if len(body_text) > TextLength.body:
        raise gr.Error(f"正文最多支持{TextLength.body}个字符")
        return

    # logger.info(title, sub_title, body_text)
    if len(title) == 0:
        raise gr.Error("主标题不能为空")
        return

    if len(prompt_text_zh) == 0 and len(prompt_text_en) == 0:
        raise gr.Error("请填写用于生成图像的提示词，或者直接点击样例填充。")
        return

    params = {
        "title": title,
        "sub_title": sub_title,
        "body": body_text,
        "prompt_text_zh": prompt_text_zh,
        "prompt_text_en": prompt_text_en,
        "text_template": text_template
    }

    logger.info(f"input params: {params}")

    # requests
    all_result_imgs = process_poster_generation(params)
    logger.info("process done.")
    return all_result_imgs


def example_func(evt: gr.SelectData):
    img_path = evt.value[0]
    # Open an image file
    with open(img_path.replace(".jpeg",".json")) as rfile:
        # Print image details
        info = json.load(rfile)
        # title, sub_title, body_text, prompt_text_zh, prompt_text_en
    return [info["title"], info["subtitle"], info["body"], info["prompt_zh"], info["prompt_en"],
            info["template"]]

def main():
    block = gr.Blocks(
        css='style.css',
        theme=gr.themes.Soft()
    ).queue(concurrency_count=2, api_open=False)
    with block:
        with gr.Row():
            # gr.HTML('', elem_id='logo')
            gr.HTML('<div id=title>PosterGenius - 创意海报生成</div>')

        with gr.Tabs() as tabs:
            collection_tab =gr.Tab(label="作品广场", elem_id='tab', id=0)
            with collection_tab:
                samples = shuffle_examples(examples_dir_idx=0)
                collection_explore_examples0 = gr.Dataset(
                    label='春节元素  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[0], x)] for x in samples
                    ],
                    samples_per_page=12,
                    elem_id='examples0',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=1)
                collection_explore_examples1 = gr.Dataset(
                    label='2D极简风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[1], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples1',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=3)
                collection_explore_examples2 = gr.Dataset(
                    label='中国刺绣风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[3], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples2',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=5)
                collection_explore_examples3 = gr.Dataset(
                    label='折纸工艺  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[5], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples3',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=4)
                collection_explore_examples4 = gr.Dataset(
                    label='中国水墨风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[4], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples4',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=2)
                collection_explore_examples5 = gr.Dataset(
                    label='3D卡通风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[2], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples5',
                    type='index', # pass index or value
                )

                ## samples2
                samples = shuffle_examples(examples_dir_idx=6)
                collection_explore_examples6 = gr.Dataset(
                    label='其它风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[6], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples6',
                    type='index', # pass index or value
                )


            creation_tab =gr.Tab(label="创作海报", elem_id='tab', id=1)
            with creation_tab:
                with gr.Column():
                    with gr.Row():
                        with gr.Column(elem_classes='column_input'):
                            title = gr.Textbox(label='主标题（可以添加换行符 \\n 强制换行）', placeholder='新年快乐', lines=2, elem_classes='title')
                            sub_title = gr.Textbox(label='副标题（可以添加换行符 \\n 强制换行）', placeholder='恭喜发财\\n万事如意', lines=2, elem_classes='sub_title')
                            body_text = gr.Textbox(label='正文（可以添加换行符 \\n 强制换行）', placeholder='春节是中国最重要的传统节日之一，每年都会吸引着数亿人回家与家人团聚。', lines=2, elem_classes='body_text')

                            prompt_text_zh = gr.Textbox(label='中文提示词',
                                                        placeholder='一只乖巧可爱的十二生肖金龙，春节氛围，水墨风，3D风格',
                                                        lines=2,
                                                        elem_classes='prompt_text_zh')
                            with gr.Accordion("高级选项", open=False, elem_id="accordion"):
                                prompt_text_en = gr.Textbox(label='英文提示词（非必填）', placeholder='',
                                                            elem_classes='prompt_text_en')
                                text_template = gr.Textbox(label='', placeholder='', visible=False, elem_classes='text_template')
                                ctrl_ratio = gr.Slider(label="图像留白强度", minimum=0, maximum=1, value=0.7)
                                ctrl_step = gr.Slider(label="图像留白步数", minimum=0, maximum=1, value=0.7)

                            with gr.Column():
                                with gr.Row():
                                    btn_ai_prompt = gr.Button(value="AI生成文案", elem_classes='btn_ai_prompt')
                                    btn = gr.Button(value="生成", elem_classes='btn_gen')
                                    # run_time = gr.Textbox(label='累计生成次数🔥🔥', value="0", interactive=False)
                                gr.Markdown("♨️ 图片较大，加载耗时，稍加等待~")
                                gr.Markdown("📌 鼠标右键保存到本地，或者在新标签页打开大图~")

                        with gr.Column():
                            # result = gr.HTML(label='preview', show_label=True, elem_classes='preview_html')
                            result_image = gr.Gallery(
                                label='preview', show_label=True, elem_classes="preview_imgs", preview=True, interactive=False)


                samples = shuffle_examples(examples_dir_idx=0)
                explore_examples0 = gr.Dataset(
                    label='春节元素  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[0], x)] for x in samples
                    ],
                    samples_per_page=12,
                    elem_id='examples0',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=1)
                explore_examples1 = gr.Dataset(
                    label='2D极简风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[1], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples1',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=3)
                explore_examples2 = gr.Dataset(
                    label='中国刺绣风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[3], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples2',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=5)
                explore_examples3 = gr.Dataset(
                    label='折纸工艺  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[5], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples3',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=4)
                explore_examples4 = gr.Dataset(
                    label='中国水墨风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[4], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples4',
                    type='index', # pass index or value
                )

                samples = shuffle_examples(examples_dir_idx=2)
                explore_examples5 = gr.Dataset(
                    label='3D卡通风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[2], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples5',
                    type='index', # pass index or value
                )

                ## samples2
                samples = shuffle_examples(examples_dir_idx=6)
                explore_examples6 = gr.Dataset(
                    label='其它风格  --  点击样例图，自动填充参数',
                    components=[gr.Image(visible=False)],
                    samples=[
                        [os.path.join(examples_dir[6], x)] for x in samples
                    ],
                    samples_per_page=8,
                    elem_id='examples6',
                    type='index', # pass index or value
                )

                with gr.Row():
                    gr.Examples(
                        label='点击自动填充输入参数',
                        examples=[
                            ["元旦快乐", "2024年1月1日", "回顾过去，展望未来，共同迎接新的一年。"],
                            ["春节快乐", "辛丑年一月三十", "春节到，祝福送，愿你幸福快乐每一天！"],
                            ["Happy Spring Festival", "Bling Bling", "Wish you happiness every day!"],
                            ["元宵节", "正月十五", "团圆时节，汤圆香甜，祝你幸福美满！"],
                            ["情人节", "爱的宣言", "让我们共度情人节。"],
                            ["情人节", "爱的宣言", "Happy Valentine's Day."],
                            ["清明节", "清明时节雨纷纷", "感恩故人\\n铭记历史"],
                            ["劳动节", "五月一日", "劳动最光荣，辛勤付出，收获美好。"],
                            ["端午节", "2024年6月5日", "送你一片艾叶粽子，团圆温馨，好运连连。祝你端午节快乐！"],
                            ["喜迎中秋", "农历八月十五", "中秋佳节，祝愿您心想事成，家庭和睦，生活幸福。"],
                            ["国之大庆\\n盛世中华", "1949 - 2023", "国庆盛世华诞\\n礼赞锦秀山河"],
                            ["国庆节", "盛世华诞·锦秀中国", "1949 - 2023"],
                            ["圣诞节快乐", "2023年12月25日", "圣诞节快乐，爱你每一天！"],
                        ],
                        inputs=[title, sub_title, body_text],
                    )
                    with gr.Column():
                        gr.Examples(
                            label='点击填入中文提示词',
                            examples=[
                                ["一只乖巧可爱的十二生肖金龙，春节氛围，水墨风，3D风格"],
                                ["中国结，腊梅，红色色调，春节氛围"],
                                ["手绘中国元素春节"],
                                ["手绘中国元素春节，饺子"],
                                ["手绘中国元素春节，街道"],
                                ["五爪金龙，中国长城，红色色调，春节氛围，水墨风"],
                                ["新年红包包装设计，红包上面有中国结"],
                                ["新年红包包装设计，红包上面有腊梅"],
                                ["中国风，剪纸灯笼，剪纸龙，云朵环绕，春节海报，高亮"],
                                ["中国风，剪纸灯笼，剪纸金龙，云朵环绕，春节海报，高亮"],
                                ["一个卡通小孩在新春里看烟花，卡通，3D"],
                                ["五爪金龙，红色色调，春节氛围，水墨风"],
                                ["一个在春节期间放烟花的快乐男孩，卡通，3D，高亮"],
                                ["太阳照射着云层，多个云朵构成了心的形状围绕一圈，红色色调，情人节"],
                            ],
                            inputs=[prompt_text_zh],
                        )

                        with gr.Accordion("更多英文提示词", open=False, elem_id="accordion"):
                            gr.Examples(
                                label='',
                                examples=[
                                    [
                                        "a large dragon,the background is the great wall,light red tones predominate, holiday poster,chinese ink painting style, minimalist style,super meticulous,8K wallpaper"],
                                    [
                                        "a beautiful chinese golden dragon flying on the sky with white clouds,the background is the great wall,light red tones predominate, holiday poster,minimalist style,super meticulous,8K wallpaper"],
                                    [
                                        "2 large lanterns on the tree,the background is the great wall,light red tones predominate, holiday poster,chinese ink painting style, minimalist style,super meticulous,8K wallpaper"],
                                    [
                                        "dumpling,Chinese knot,Wintersweet,spring festival,red tones,minimalist style,super meticulous,8K wallpaper"],
                                    [
                                        "Spring couplets with beautiful Chinese knot,spring festival atmosphere,chinese ink painting style,minimalist style,original,8K wallpaper,an extremely delicate and beautiful,artbook"],
                                    [
                                        "New Year countdown clock on the sky with firecrackers,red tones,minimalist style,super meticulous,8K wallpaper"],
                                    [
                                        "New Year's cards with beautiful Chinese knot,New Year atmosphere,minimalist style,original,8K wallpaper,an extremely delicate and beautiful,artbook"],
                                    [
                                        "Snowflakes celebrate new year,New Year atmosphere,minimalist style,original,8K wallpaper,an extremely delicate and beautiful"],
                                    ["2024 Calendar page,snowflake,minimalist style,super meticulous,8K wallpaper"],
                                    ["Timer,snowflake,minimalist style,super meticulous,8K wallpaper"],
                                    [
                                        "2 mooncakes,moon,holiday poster,mid-autumn festival atmosphere,osmanthus tree,chinese ink painting style,minimalist style,original,8K wallpaper,an extremely delicate and beautiful,artbook"],
                                    [
                                        "cute cartoon rabit is watching an open book, in the style of luminous and dreamlike scenes, joyful celebration of nature, eye-catching composition, naturalistic depictions of flora and fauna, high quality photo"],

                                ],
                                inputs=[prompt_text_en],
                            )

                collection_explore_examples0.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ]) 

                collection_explore_examples1.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ]) 

                collection_explore_examples2.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])

                collection_explore_examples3.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])

                collection_explore_examples4.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])

                collection_explore_examples5.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])

                collection_explore_examples6.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])

                explore_examples0.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ]) 

                explore_examples1.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ]) 

                explore_examples2.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])

                explore_examples3.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])

                explore_examples4.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])

                explore_examples5.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])

                explore_examples6.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template
                ])



        btn.click(generate, inputs=[title, sub_title, body_text, prompt_text_zh, prompt_text_en, text_template],
                  outputs=[result_image])
        btn_ai_prompt.click(generate_text, inputs=[title], outputs=[sub_title, body_text])

    logger.info("============ Launch Client ============")
    block.launch(server_name=socket.gethostbyname(socket.gethostname()) if os.getenv('SERVER_IP') else '127.0.0.1',
                 root_path=f"/{os.getenv('GRADIO_PROXY_PATH')}" if os.getenv(
                     'GRADIO_PROXY_PATH') else "",
                server_port=8888 if os.getenv('SERVER_IP') else None,
                share=False)

if __name__ == '__main__':
    main()
