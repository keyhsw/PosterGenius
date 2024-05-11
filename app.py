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
examples_dir = ['example/pick4','example/pick3','example/pick2', 'example/春节', 'example/2D插画3','example/中国刺绣','example/中国水墨','example/折纸工艺','example/真实场景']
examples_dir_lables = ['近期更新--横版','近期更新--竖版','节气海报', '春节', '2D插画3', '中国刺绣','中国水墨','折纸工艺','真实场景']
random.seed(100)

def shuffle_examples(examples_dir_idx=0):
    ## samples0
    samples = []
    for ff in os.listdir(examples_dir[examples_dir_idx]):
        if ff.endswith(".jpeg"):
            samples.append(ff)
        if ff.endswith(".png"):
            samples.append(ff)
    random.shuffle(samples)
    return samples


def generate(title, sub_title, body_text, prompt_text_zh, prompt_text_en, text_template,wh_ratios,lora_name,lora_weight,ctrl_ratio,ctrl_step):
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
        "text_template": text_template,
        "wh_ratios":wh_ratios,
        "lora_name":lora_mapping[lora_name],
        "lora_weight":lora_weight,
        "ctrl_ratio":ctrl_ratio,
        "ctrl_step":ctrl_step,
        "sr_flag":False,
        "bg_image_urls":"",
        "render_params":"",
    }

    logger.info(f"input params: {params}")

    # requests
    all_result_imgs,bg_image_urls,render_params = process_poster_generation(params)
    logger.info("process done.")
    bg_image_urls.append("")
    render_params.append("")
    return all_result_imgs, "",bg_image_urls,render_params

def generate_sr(bg_image_urls,render_params):
    if bg_image_urls == None or render_params == None:
        raise gr.Error(f"请先生成再进行分辨率提升")
        return
    if bg_image_urls[4] == "" or render_params[4] == "":
        raise gr.Error(f"请选中一张图片再进行分辨率提升")
        return
    params = {
        "title": "",
        "sub_title": "",
        "body": "",
        "prompt_text_zh": "",
        "prompt_text_en": "",
        "text_template": "",
        "wh_ratios":"",
        "lora_name":"",
        "lora_weight":"",
        "ctrl_ratio":"",
        "ctrl_step":"",
        "sr_flag":True,
        "bg_image_urls":bg_image_urls[4],
        "render_params":render_params[4],

    }

    logger.info(f"input params: {params}")

    # requests
    all_result_imgs,_,_ = process_poster_generation(params)
    logger.info("process done.")
    return all_result_imgs, ""

def update_state(evt: gr.SelectData,urls,reder_paras):
    index = evt.index
    urls[4] = urls[index]
    reder_paras[4] = reder_paras[index]
    return urls,reder_paras
def example_func(evt: gr.SelectData):
    img_path = evt.value[0]
    json_name = img_path.replace(".render.png",".json")
    json_name = json_name.replace(".png",".json")
    json_name = json_name.replace(".jpeg",".json")
    label_name = img_path.split('/')[-2]
    # Open an image file
    with open(json_name) as rfile:
        # Print image details
        info = json.load(rfile)
        # title, sub_title, body_text, prompt_text_zh, prompt_text_en
    gr.Info("已将配方发送到创作页面")
    lora_name = info.get("lora_name","不指定")
    if lora_name == "不指定" and label_name in lora_mapping.keys():
        lora_name = label_name
    lora_weight = info.get("lora_weight",0.5)
    ctrl_ratio = info.get("ctrl_ratio",0.7)
    ctrl_step = info.get("ctrl_step",0.7)
    wh_ratios = info.get("wh_ratios","竖版")
    return [info["title"], info["subtitle"], info["body"], info["prompt_zh"], info["prompt_en"],
            info["template"],lora_name,float(lora_weight),float(ctrl_ratio),float(ctrl_step),wh_ratios, gr.Tabs.update(selected=1)]


lora_mapping = {
    "2D插画1":"2D插画1",
    "2D插画2":"2D插画2",
    "2D插画3":"2D极简",
    "3D卡通1":"3D卡通1",
    #"3D卡通2":"3D卡通2",
    "浩瀚星云":"浩瀚星云",
    "浓郁色彩":"浓郁色彩",
    "光线粒子":"光线粒子",
    "透明玻璃":"透明玻璃",
    #"简约线条":"简约线条",
    #"几何方块":"几何方块",
    "剪纸工艺":"剪纸工艺",
    "折纸工艺":"折纸工艺",
    "中国水墨":"中国水墨",
    "中国刺绣":"中国刺绣",
    "真实场景":"真实场景",
    "复古油画":"复古油画",
    "不指定":"",
    }


style_image_mapping = {
    "3D卡通1":"3D.jpg",
    #"3D卡通2":"3D.jpg",
    "浩瀚星云":"xingyun.jpg",
    "浓郁色彩":"secai.jpg",
    "复古油画":"youhua.jpg",
    "剪纸工艺":"jianzhi.jpg",
    "折纸工艺":"zhezhi.jpg",
    "光线粒子":"guangxian.jpg",
    "透明玻璃":"boli.jpg",
    "2D插画1":"2D1.jpg",
    "2D插画2":"2D2.jpg",
    "2D插画3":"2D3.jpg",
    #"简约线条":"cixiu.jpg",
    #"几何方块":"cixiu.jpg",
    "中国水墨":"shuimo.jpg",
    "中国刺绣":"cixiu.jpg",
    "真实场景":"zhenshi.jpg",
    "不指定":None,
    }

def return_style_exsample(selected_label):
    if selected_label !="不指定":
        examples_dir = f"example/风格展示/{style_image_mapping[selected_label]}"

        return examples_dir
    else:
        return None

def erasure_template():
    return ""


def create_example(label, idx):
    samples = shuffle_examples(examples_dir_idx=idx)
    if "近期更新--竖版" in label:
        show_num = 12
    else:
        show_num = 6
    examples = gr.Dataset(
        label=f'{label}  --  点击样例图，自动填充参数',
        components=[gr.Image(visible=False)],
        samples=[
            [os.path.join(examples_dir[idx], x)] for x in samples
        ],
        samples_per_page=show_num,
        elem_id=f'{label}_{idx}',
        type='index', # pass index or value
    )
    return examples

def main():
    block = gr.Blocks(
        css='style.css',
        theme=gr.themes.Soft()
    ).queue(concurrency_count=10, api_open=False)
    with block:
        with gr.Row():
            # gr.HTML('', elem_id='logo')
            gr.HTML('<div id=title>PosterGenius - 创意海报生成</div>')

        with gr.Tabs() as tabs:
            collection_tab =gr.Tab(label="作品广场", elem_id='tab', id=0)
            with collection_tab:
                collection_explore_examples = []
                for idx, label in enumerate(examples_dir):
                    label = examples_dir_lables[idx]
                    exps = create_example(label, idx)
                    collection_explore_examples.append(exps)

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
                            
                            with gr.Row():
                                styles = gr.Radio(label="生成风格选择（非必选）",choices=list(lora_mapping.keys()),value = "不指定")
                                with gr.Column():
                                    style_example = gr.Image(label="风格示例", show_label=True, elem_classes="style_example_img", show_download_button=False)
                                    wh_ratios = gr.Radio(label="宽高比选择",choices=["横版","竖版"],value="横版")
                            

                            
                            styles.change(return_style_exsample,inputs=[styles],outputs=[style_example])

                            with gr.Accordion("高级选项", open=False, elem_id="accordion"):
                                prompt_text_en = gr.Textbox(label='英文提示词（非必填）', placeholder='',
                                                            elem_classes='prompt_text_en')
                                text_template = gr.Textbox(label='', placeholder='', visible=False, elem_classes='text_template')
                                lora_weight = gr.Slider(minimum=0.3, maximum=0.8, step=0.05, value=0.8, label="风格权重选择（权重越大，风格越明显）",interactive=True)
                                ctrl_ratio = gr.Slider(label="图像留白强度（留白强度越高，留白效果越好，但对背景生成效果可能有负面影响）", minimum=0.3, maximum=0.8,step=0.05, value=0.7)
                                ctrl_step = gr.Slider(label="图像留白步数（留白步数越高，留白效果越好，但对背景生成效果可能有负面影响）", minimum=0.3, maximum=0.8, step=0.05,value=0.7)
                            wh_ratios.change(erasure_template,outputs=[text_template])
                            with gr.Column():
                                with gr.Row():
                                    btn_ai_prompt = gr.Button(value="AI生成文案", elem_classes='btn_ai_prompt')
                                    btn = gr.Button(value="生成", elem_classes='btn_gen')
                                    # run_time = gr.Textbox(label='累计生成次数🔥🔥', value="0", interactive=False)
                                gr.Markdown("♨️ 图片较大，加载耗时，稍加等待~")
                                gr.Markdown("📌 鼠标右键保存到本地，或者在新标签页打开大图~")

                        with gr.Column():
                            # result = gr.HTML(label='preview', show_label=True, elem_classes='preview_html')
                            bg_image_urls = gr.State()
                            render_params = gr.State()
                            result_image = gr.Gallery(
                                label='preview', show_label=True, elem_classes="preview_imgs", preview=True, interactive=False)
                            btn_sr = gr.Button(value="提升结果分辨率", elem_classes='btn_sr')
                            result_image.select(fn=update_state,inputs=[bg_image_urls,render_params],outputs=[bg_image_urls,render_params])
                            result_sr_image = gr.Gallery(
                                label='高分辨率结果', show_label=True, elem_classes="preview_sr_imgs", preview=True, interactive=False)



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

                with gr.Row():
                    # 钉钉群二维码信息
                    gr.HTML(f"""
                            <div id=qr_code>
                                    <img id=qr_code  src='https://modelscope.cn/api/v1/studio/iic/PosterGenius/repo?Revision=master&FilePath=assets/qrcode_dd.jpg&View=true'>
                            </div>
                            <div id=qr_code_info>
                                创意海报需求共建钉钉群
                            </div>
                    """)
                    gr.HTML(f"""
                            <div id=qr_code>
                                    <img id=qr_code  src='https://modelscope.cn/api/v1/studio/iic/PosterGenius/repo?Revision=master&FilePath=assets/qrcode_wx.jpg&View=true'>
                            </div>
                            <div id=qr_code_info>
                                创意海报需求共建微信群
                            </div>
                    """)

            for exps in collection_explore_examples:
                exps.select(fn=example_func, outputs=[
                    title, sub_title, body_text,
                    prompt_text_zh, prompt_text_en, text_template,styles,lora_weight,ctrl_ratio,ctrl_step,wh_ratios, tabs
                ]) 



        btn.click(generate, inputs=[title, sub_title, body_text, prompt_text_zh, prompt_text_en, text_template,wh_ratios,styles,lora_weight,ctrl_ratio,ctrl_step],
                  outputs=[result_image, text_template,bg_image_urls,render_params])
        btn_ai_prompt.click(generate_text, inputs=[title], outputs=[sub_title, body_text])
        btn_sr.click(generate_sr,inputs=[bg_image_urls,render_params],outputs=[result_sr_image, text_template])

    logger.info("============ Launch Client ============")
    block.launch(server_name=socket.gethostbyname(socket.gethostname()) if os.getenv('SERVER_IP') else '127.0.0.1',
                 root_path=f"/{os.getenv('GRADIO_PROXY_PATH')}" if os.getenv(
                     'GRADIO_PROXY_PATH') else "",
                server_port=8888 if os.getenv('SERVER_IP') else None,
                share=False)

if __name__ == '__main__':
    main()
