from os import getenv

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import Response
from uvicorn import run as uvicorn_run

load_dotenv()

app = FastAPI()

origins = getenv('ALLOWED_ORIGINS').split(',') if getenv('ALLOWED_ORIGINS') else ['*']
hosts = getenv('ALLOWED_HOSTS').split(',') if getenv('ALLOWED_HOSTS') else ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=hosts
)


@app.get("/{username}/contributions")
async def get_svg(
        username: str,
        text_color: str = 'white',
        level_0: str = '#161b22',
        level_1: str = '#0e4429',
        level_2: str = '#006d32',
        level_3: str = '#26a641',
        level_4: str = '#39d353',
        get_image: bool = False
):
    """
    Args:
        username: GitHub username to fetch data from
        text_color: the color for the caption (months and weekday)
        level_0: first color of the gradient
        level_1: second color of the gradient
        level_2: third color of the gradient
        level_3: fourth color of the gradient
        level_4: fith color of the gradient
        get_image: if true returns the .svg image
    Returns:

    """
    levels = {
        0: level_0,
        1: level_1,
        2: level_2,
        3: level_3,
        4: level_4
    }
    async with ClientSession() as session:
        async with session.get(f'https://github.com/users/{username}/contributions') as response:
            raw_response = await response.text()

            soup = BeautifulSoup(raw_response, features='html.parser')
            svg = soup.select_one('.js-calendar-graph-svg')
            width = svg.get('width')
            height = svg.get('height')
            contributions = soup.find('h2')

            svg['style'] = 'overflow: scroll'
            svg['xmlns'] = 'http://www.w3.org/2000/svg'
            del svg['height']
            svg['width'] = '100%'

            if not get_image:
                svg.append(
                    BeautifulSoup(
                        '''<div id="tooltip" 
                        style="position: absolute; 
                        display: none; 
                        background-color: #6e7680; 
                        border-radius: .4em; 
                        font-size: .85em;
                        padding: 8px"
                        ></div>''',
                        'html.parser')
                )
            texts = svg.select('text')
            for index, text in enumerate(texts):
                if text.get('dy') in ['8', '32', '57', '81']:
                    text['style'] = 'display: none'
                else:
                    if index > 0 and texts[index].get('x'):
                        if int(texts[index].get('x')) - int(texts[index - 1].get('x')) < 27:
                            texts[index - 1]['style'] = 'display: none'
                    text['fill'] = text_color
                    text['shape-rendering'] = 'crispedges'
                    if get_image:
                        text['style'] = 'font-family: "Roboto", "-apple-system", ' \
                                        '"Helvetica Neue", Helvetica, Arial, sans-serif; ' \
                                        'font-size: 14px; line-height: 1.5'
            months = svg.select('g g')
            for month in months:
                if get_image:
                    month['style'] = 'font-family: "Roboto", "-apple-system", ' \
                                    '"Helvetica Neue", Helvetica, Arial, sans-serif; ' \
                                     'font-size: 14px; line-height: 1.5'
                week = month.select('rect')
                for day in week:
                    day['fill'] = levels.get(int(day.get('data-level')))
    if not get_image:
        return {
            'svg': str(svg),
            'contributions': contributions.get_text()
        }
    del svg['style']
    svg['height'] = height
    svg['width'] = width
    new_svg = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' + str(svg)
    return Response(
        str(new_svg),
        200,
        media_type='image/svg+xml'
    )


if __name__ == "__main__":
    uvicorn_run(
        "src.app:app",
        host="0.0.0.0",
        workers=4,
        port=int(getenv('PORT', 10000)),
        log_level="info",
        reload=True,
    )
