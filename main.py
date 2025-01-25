from fastapi import FastAPI, HTTPException
import smtplib
from email.mime.text import MIMEText
from random import randint
import uvicorn
from Models import *
import os
import anyio
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from prometheus_client import start_http_server
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.metrics import CallbackOptions, Observation, get_meter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from typing import Iterable
import psutil
import json
import logging


use_logger = False

app = FastAPI()
users_db = {}

reader = PrometheusMetricReader()
provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter(__name__)

def setup_otel():
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()
    
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    jaeger_exporter = JaegerExporter(
        agent_host_name='localhost', 
        agent_port=6831,             
    )
    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    FastAPIInstrumentor().instrument_app(app)
    LoggingInstrumentor().instrument(set_logging_format=True)


def cpu_persent_measure(options: CallbackOptions) -> Iterable[Observation]:
    return [Observation(psutil.cpu_percent(interval=0.1))]


def memory_percent_measure(options: CallbackOptions) -> Iterable[Observation]:
    process = psutil.Process()
    mem_info = process.memory_info()
    return [Observation(mem_info.vms / (1024))]

# Метрики использования ресурсов
cpu_usage = meter.create_observable_gauge(
    name="cpu_usage_percent",
    description="Процент использования CPU",
    callbacks=[cpu_persent_measure],
)

memory_usage = meter.create_observable_gauge(
    name="memory_usage_percent",
    description="Процент использования памяти",
    callbacks=[memory_percent_measure],
)

setup_otel()

# Запуск сервера Prometheus для экспонирования метрик
start_http_server(8000)
print("Метрики доступны по адресу http://localhost:8000/metrics")



def setup_otel():
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()
    
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    FastAPIInstrumentor().instrument_app(app)
    LoggingInstrumentor().instrument(set_logging_format=True)


def send_verification_email(email: str, code: str):
    sender_email = os.environ["sender_email"]
    sender_password = os.environ["sender_password"]

    msg = MIMEText(f'Ваш код подтверждения: {code}')
    msg['Subject'] = 'Код подтверждения'
    msg['From'] = sender_email
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())


@app.post("/login")
def login(user: UserLogin):
    logger = logging.getLogger(__name__)
    logger.info("login")
    db_user = users_db.get(user.email)
    if not db_user or db_user["password"] != user.password or not db_user["is_verified"]:
        raise HTTPException(status_code=400, detail="Неверные учетные данные или email не подтвержден")

    return HTTPException(status_code=200, detail="Вход выполнен успешно!")


@app.post("/delete")
def delete(user: UserLogin):
    logger = logging.getLogger(__name__)
    logger.info("delete")
    db_user = users_db.get(user.email)
    if not db_user or db_user["password"] != user.password:
        raise HTTPException(status_code=400, detail="Неверные учетные данные")

    users_db.pop(user.email)
    return HTTPException(status_code=200, detail="Аккаунт удален!")


@app.post("/register")
def register(user: UserCreate):
    logger = logging.getLogger(__name__)
    logger.info("register")
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email уже подтвержден")

    verification_code = str(randint(100000, 999999)) if user.email != test_email else test_code
    users_db[user.email] = {
        "password": user.password,
        "is_verified": False,
        "verification_code": verification_code
    }

    send_verification_email(user.email, verification_code)
    return HTTPException(status_code=200, detail="Пользователь зарегистрирован. "
                                                 "Проверьте вашу почту для подтверждения кода")


@app.post("/verify")
def verify(user: UserVerify):
    logger = logging.getLogger(__name__)
    logger.info("verify")
    user_db = users_db.get(user.email)
    if not user_db or user_db["verification_code"] != user.code:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")

    user_db["is_verified"] = True
    return HTTPException(status_code=200, detail="Email подтвержден!")


@app.post("/reset-password/request")
def reset_password_request(request: PasswordResetRequest):
    logger = logging.getLogger(__name__)
    logger.info("reset_password_request")
    user = users_db.get(request.email)
    if not user or user["password"] != request.old_password:
        raise HTTPException(status_code=400, detail="Неверные учетные данные")

    verification_code = str(randint(100000, 999999)) if request.email != test_email else test_code
    user["verification_code"] = verification_code
    send_verification_email(request.email, verification_code)
    return HTTPException(status_code=200, detail="Код подтверждения отправлен на почту")


@app.post("/reset-password/confirm")
def reset_password_confirm(request: PasswordResetConfirm):
    logger = logging.getLogger(__name__)
    logger.info("reset_password_confirm")
    user = users_db.get(request.email)
    if not user or user["verification_code"] != request.code:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")

    user["password"] = request.new_password
    return HTTPException(status_code=200, detail="Пароль успешно изменен!")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")