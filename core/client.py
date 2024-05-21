from http import HTTPStatus
import json
import os
import random
import time
from dashscope import Generation
import requests
import gradio as gr
import concurrent.futures
from PIL import Image
import io


from core.log import logger

APP_AUTH_GENERAL_POSTER = os.getenv('APP_AUTH_GENERAL_POSTER')


def download_img_pil(index, img_url):
    # print(img_url)
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        img = Image.open(io.BytesIO(r.content))
        return (index, img)
    else:
        logger.error(f"Fail to download: {img_url}")



def download_images(img_urls, batch_size):
    imgs_pil = [None] * batch_size
    # worker_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        to_do = []
        for i, url in enumerate(img_urls):
            future = executor.submit(download_img_pil, i, url)
            to_do.append(future)

        for future in concurrent.futures.as_completed(to_do):
            ret = future.result()
            # worker_results.append(ret)
            index, img_pil = ret
            imgs_pil[index] = img_pil  # 按顺序排列url，后续下载关联的图片或者svg需要使用

    return imgs_pil


class GeneratePoster:
    def __init__(self) -> None:
        self.url_create_task = 'https://poc-dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'

    def query_result(self, task_id, headers):
        # 异步查询, 一个task_id可能有多张图片
        is_running = True
        while is_running:
            # url_query = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
            # url_query = f'https://poc-dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
            self.url_query_task = f'https://poc-dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
            res_ = requests.post(self.url_query_task, headers=headers)

            respose_code = res_.status_code
            if 200 == respose_code:
                res = json.loads(res_.content.decode())
                if "SUCCEEDED" == res['output']['task_status']:
                    logger.info(f"task_id: {task_id}: general poster generation task query success.")
                    img_urls = res['output']['render_urls']
                    bg_image_urls = res['output']['image_urls']
                    render_params = res['output']['render_params']
                    # img_urls = [x['url'] for x in img_urls]
                    logger.info(f'task_id: {task_id}: task result: {res_.content.decode("utf-8")}')
                    break
                elif "FAILED" != res['output']['task_status']:
                    logger.debug(f"task_id: {task_id}: query result...")
                    time.sleep(5)
                else:
                    raise gr.Error(f'[ERROR] {res["output"]["message"]}')
            elif 429 == respose_code:
                logger.info(f'task_id: {task_id}: Requests rate limit exceeded, please try again later')
                time.sleep(2)
            else:
                logger.error(f'task_id: {task_id}: Fail to query task result: {res_.content} httpcode:{respose_code}')
                raise gr.Error("Fail to query task result.")

        return (img_urls,bg_image_urls,render_params, task_id)

    def request(self, args):
        title = args.get("title")
        sub_title = args.get("sub_title")
        body = args.get("body")
        prompt_text_zh = args.get("prompt_text_zh")
        prompt_text_en = args.get("prompt_text_en")
        text_template = args.get("text_template") 
        wh_ratios = args.get("wh_ratios") 
        lora_name = args.get("lora_name") 
        lora_weight = args.get("lora_weight") 
        ctrl_ratio = args.get("ctrl_ratio") 
        ctrl_step = args.get("ctrl_step")
        sr_flag = args.get("sr_flag")  
        bg_image_urls = args.get("bg_image_urls")  
        render_params = args.get("render_params")  
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {APP_AUTH_GENERAL_POSTER}" ,
            "X-DashScope-Async": "enable",
            "X-DashScope-DataInspection": "enable"
        }
        model = "pre-general_poster-1520"
        payload = {
                "model": model,
                "input":{
                    "title": title,
                    "sub_title": sub_title,
                    "body_text": body,
                    "prompt_text_zh":prompt_text_zh,
                    "prompt_text_en": prompt_text_en,
                    "text_template":text_template,
                    "wh_ratios":wh_ratios,
                    "lora_name":lora_name,
                    "lora_weight":lora_weight,
                    "ctrl_ratio":ctrl_ratio,
                    "ctrl_step":ctrl_step,
                    "sr_flag":sr_flag,
                    "bg_image_urls":bg_image_urls,
                    "render_params":render_params,
                },
                "parameters": {
                }
            }
        res_ = requests.post(self.url_create_task, data=json.dumps(payload), headers=headers)
        logger.info(f"Create general poster task: {payload}")

        respose_code = res_.status_code
        if 200 == respose_code:
            res = json.loads(res_.content.decode())
            request_id = res['request_id']
            task_id = res['output']['task_id']
            logger.info(f"request_id: {request_id}: Create general poster task done. res: {res}")
        else:
            logger.error(f'Fail to create general poster task: {res_.content}')
            raise gr.Error("Fail to create general poster task.")

        # Query task results
        result_image_urls,result_bg_image_urls,result_render_params,_ = self.query_result(task_id, headers)
        

        # Download result images
        logger.info(f"request_id: {request_id}: download generated general poster images.")
        img_data = download_images(result_image_urls, len(result_image_urls))
        logger.info(f"request_id: {request_id}: Generate general poster done.")
        return img_data,result_bg_image_urls,result_render_params,result_image_urls
    
    def request_local(self, args):
        title = args.get("title")
        sub_title = args.get("sub_title")
        body = args.get("body")
        prompt_text_zh = args.get("prompt_text_zh")
        prompt_text_en = args.get("prompt_text_en")
        text_template = args.get("text_template") 
        wh_ratios = args.get("wh_ratios") 
        lora_name = args.get("lora_name") 
        lora_weight = args.get("lora_weight") 
        ctrl_ratio = args.get("ctrl_ratio") 
        ctrl_step = args.get("ctrl_step") 
        sr_flag = args.get("sr_flag")  
        bg_image_urls = args.get("bg_image_urls")  
        render_params = args.get("render_params")
        user_mask = args.get("user_mask")
        image_prompt = args.get("image_prompt")
        image_prompt_weight = args.get("image_prompt_weight")  
        body = {
            "header" : {
            "request_id":"9B49478D-DB34-5B92-BB6C-5F666653D053",
            "service_id":"3862b8df",
            "task_id":"9B49478D-DB34-5B92-BB6C-5F666653D053",
            "attributes":{
            "user_id": "1234567890"
                }
            },
            "payload" : {
                "input":{
                    "title": title,
                    "sub_title": sub_title,
                    "body_text": body,
                    "prompt_text_zh":prompt_text_zh,
                    "prompt_text_en": prompt_text_en,
                    "text_template":text_template,
                    "wh_ratios":wh_ratios,
                    "lora_name":lora_name,
                    "lora_weight":lora_weight,
                    "ctrl_ratio":ctrl_ratio,
                    "ctrl_step":ctrl_step,
                    "sr_flag":sr_flag,
                    "bg_image_urls":bg_image_urls,
                    "render_params":render_params,
                    "user_mask":user_mask, 
                    "image_prompt":image_prompt,
                    "image_prompt_weight":image_prompt_weight,
                },
                "parameters": {
                }
            }
        }
        response = requests.post('http://127.0.0.1:8090/api/predict/service_name', headers={}, json=body).json()

        #outputs = response["payload"]["output"]["image_urls"]
        outputs = response
        result_image_urls = outputs['payload']['output']['render_urls']
        result_bg_image_urls = outputs['payload']['output']['image_urls']
        result_render_params = outputs['payload']['output']['render_params']
        # Download result images
        test = 100
        img_data = download_images(result_image_urls, len(result_image_urls))
        return img_data,result_bg_image_urls,result_render_params,result_image_urls


class GeneratePromptQwen:
    def __init__(self) -> None:
        pass

    def generate_chat(self, input: str):
        print(f'Generate AI Prompt with: {input}')
        messages = [
            {'role': 'user', 'content': input}]
        gen = Generation()
        temperature=random.uniform(1.0, 1.5)
        top_p=random.uniform(0.2, 0.8)
        response = gen.call(
            'qwen-14b-chat',
            messages=messages,
            result_format='message',  # set the result is message format.
            temperature=temperature,
            top_p=top_p,
        )
        if response.status_code == HTTPStatus.OK:
            concept = response.output.choices[0].message.content
            print(f'Generate AI Prompt: {concept}')
            return concept
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            print(f'Fail to generate prompt, msg: {response.message}')




