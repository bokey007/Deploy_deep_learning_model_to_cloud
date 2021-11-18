FROM python:3.6
LABEL Author="Sudhir"
ENV FLASK_APP "login_reg"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG True
RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/
COPY ./alexnet-owt-4df8aa71.pth /root/.cache/torch/checkpoints/alexnet-owt-4df8aa71.pth
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
ADD . /app
EXPOSE 5000

CMD flask run --host=0.0.0.0

