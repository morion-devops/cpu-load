FROM python:3.10
RUN pip install cpu-load-generator

CMD python -m cpu_load_generator -l 0.5 -d 20 -c -1