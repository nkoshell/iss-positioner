FROM nkoshell/iss-positioner
MAINTAINER nkoshell <nikita.koshelev@gmail.com>

EXPOSE 80

WORKDIR /opt/iss-positioner/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD . ./

CMD python -m server
