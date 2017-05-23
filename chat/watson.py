# -*- coding: utf-8 -*-
import json
import sys
import requests
from channels import Group
from bs4 import BeautifulSoup
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator
from watson_developer_cloud import ToneAnalyzerV3 as ToneAnalyzer
from watson_developer_cloud import VisualRecognitionV3 as VisualRecognition

language_translator = LanguageTranslator(
    username='<your key token pasted here>',
    password='<your key token pasted here>'
)

visual_recognition = VisualRecognition(
    version='2016-05-20',
    api_key='<your key token pasted here>'
)

tone_analyzer = ToneAnalyzer(
    version='2016-05-19',
    username='<your key token pasted here>',
    password='<your key token pasted here>'
)


def send_channel_message(room, label, channel_layer, message, context):
    data = {'handle': 'Watson', 'message': message}
    m = room.messages.create(**data)
    text = json.dumps(m.as_dict())
    room.context = json.dumps(context)
    room.save()
    Group('chat-'+label, channel_layer=channel_layer).send({'text': text})


def send_message_to_watson(room, conversation, channel_layer, command, label, context):
    print("context:\n" + json.dumps(context, indent=2))

    try:
        response = conversation.message(
            workspace_id='1a16678b-41a7-4401-b24d-69ffdf4f1e7c',
            message_input={'text': command},
            context=context
        )
        context = response['context']
    except:
        message = "죄송합니다. 왓슨 대화처리기에서 에러가 발생하였습니다.\n"
        send_channel_message(room, label, channel_layer, message, context)
        print(sys.exc_info()[0])
        return

    print("response:\n" + json.dumps(response, indent=2))
    print("command:" + command + " intent:" + (response['intents'][0]['intent'] if response['intents'] else 'None'))

    message = response['output']['text'][0]
    visited_node_count = len(response['output']['nodes_visited'])
    current_node = response['output']['nodes_visited'][visited_node_count-1]
    print("current node:" + current_node)
    send_channel_message(room, label, channel_layer, message, context)

    region = None
    if response['entities'] and response['entities'][0]['entity'] == "Region":
        region = response['entities'][0]['value']

    if current_node.startswith('미세먼지결과') and region:
        base_date, air_info = crawl_air_info(region)
        message = base_date + " 기준으로,\n미세먼지 수치는 " + air_info[1] + "이며 통합대기지수는 " + air_info[7] + "상태입니다."
        send_channel_message(room, label, channel_layer, message, context)

    if current_node.startswith('번역결과'):
        message = translate(command, response['context']['language'])
        send_channel_message(room, label, channel_layer, message, context)

    if current_node.startswith('이미지분석결과'):
        message = analyze_image(command[1:-1], response['context']['image'])
        send_channel_message(room, label, channel_layer, message, context)

    if current_node.startswith('톤분석결과'):
        message = analyze_tone(command)
        send_channel_message(room, label, channel_layer, message, context)


def crawl_air_info(region):
    request = requests.get("http://cleanair.seoul.go.kr/air_city.htm?method=measure&citySection=CITY")
    soup = BeautifulSoup(request.content, "html.parser", from_encoding="utf-8")

    date = soup.find('h4', 'mgb10').text
    base_date = date[date.index(':') + 2:].strip()

    seoul_air_info = {}
    rows = soup.find('table', 'tbl2').find_all('tr')
    for row in rows:
        cols = [col.text.strip() for col in row.find_all('td')]
        if cols:
            seoul_air_info[cols[0]] = cols

    return base_date, seoul_air_info[region]


def translate(text, target_language):
    source = 'en'
    target = 'ko'

    if target_language == '영어':
        source, target = target, source

    try:
        translation = language_translator.translate(
            text=text,
            source=source,
            target=target
        )
    except:
        return "죄송합니다. 왓슨 번역기에서 문제가 발생했습니다. 다시 시도해 주세요."

    return translation


def analyze_image(image_url, image_type):
    result_text = ""
    if image_type == "전체":
        image_response = visual_recognition.classify(
            images_url=image_url
        )
    elif image_type == "얼굴":
        image_response = visual_recognition.detect_faces(
            images_url=image_url
        )
    print("image response:\n" + json.dumps(image_response, indent=2))
    if "error" in image_response['images'][0]:
        return "이미지 분석중 다음의 에러가 발생하였습니다.\n" + image_response['images'][0]['error']['description']

    if image_type == "전체":
        classes = image_response['images'][0]['classifiers'][0]['classes']
        for keyword in classes:
            result_text += "- {} ({}%)\n".format(keyword['class'], round(keyword['score'] * 100))
        print("result:" + result_text)
        return result_text

    if image_type == "얼굴":
        faces = image_response['images'][0]['faces']
        if not faces:
            return "죄송해요. 사람얼굴을 찾지 못했어요. ^^;;"
        for info in faces:
            age = "나이: {}~{}세 (확률 {}%)\n".format((info['age']['min'] if 'min' in info['age'] else ""),
                                                 (info['age']['max'] if 'max' in info['age'] else ""),
                                                 round(info['age']['score'] * 100))
            gender = "성별: {} (확률 {}%)\n".format(info['gender']['gender'],
                                                round(info['gender']['score'] * 100))
            identity = ""
            if 'identity' in info:
                identity = "이름: {} (확률 {}%)\n".format(info['identity']['name'],
                                                      round(info['identity']['score'] * 100))
            result_text += age + gender + identity
        return result_text

    return ""


def analyze_tone(text):
    result_text = ""
    try:
        tone_response = tone_analyzer.tone(text=text)
    except:
        return "죄송합니다. 왓슨 톤분석기에서 에러가 발생했습니다."
    tone_categories = tone_response['document_tone']['tone_categories']
    print("tone_categories:\n" + json.dumps(tone_categories, indent=2))
    for category in tone_categories:
        result_text += "- 분석유형 : {}\n".format(category['category_name'])
        for tone in category['tones']:
            result_text += "   : {} ({}%)\n".format(tone['tone_name'], round(tone['score'] * 100))

    return result_text

