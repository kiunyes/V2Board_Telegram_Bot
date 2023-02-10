FROM python:3.12-rc-alpine AS build
ADD ./V2Board_Python_Bot/requirements.txt /build/requirements.txt
WORKDIR /build
RUN apk update
RUN apk add --no-cache --virtual .build-deps git build-base libffi-dev libstdc++
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt
RUN apk del .build-deps

FROM python:3.12-rc-alpine
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
RUN apk update
RUN apk add --no-cache libstdc++
ADD V2Board_Python_Bot /V2Board_Python_Bot
WORKDIR /V2Board_Python_Bot
CMD ["python3","bot.py"]