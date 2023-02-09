FROM python:3.8-alpine AS build
ADD ./requirements.txt /build/requirements.txt
WORKDIR /build
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories
RUN apk update
RUN apk add --no-cache --virtual .build-deps git build-base libffi-dev libstdc++
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt
RUN apk del .build-deps

FROM python:3.8-alpine
COPY --from=build /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
RUN apk add --no-cache libstdc++
ADD V2Board_Python_Bot /V2Board_Python_Bot
WORKDIR /V2Board_Python_Bot
CMD ["python3","bot.py"]