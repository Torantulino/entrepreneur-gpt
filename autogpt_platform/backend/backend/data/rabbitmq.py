import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Awaitable, Optional

import aio_pika
import pika
import pika.adapters.blocking_connection
from pika.spec import BasicProperties
from pydantic import BaseModel

from backend.util.retry import conn_retry
from backend.util.settings import Settings

logger = logging.getLogger(__name__)


class ExchangeType(str, Enum):
    DIRECT = "direct"
    FANOUT = "fanout"
    TOPIC = "topic"
    HEADERS = "headers"


class Exchange(BaseModel):
    name: str
    type: ExchangeType
    durable: bool = True
    auto_delete: bool = False


class Queue(BaseModel):
    name: str
    durable: bool = True
    auto_delete: bool = False
    # Optional exchange binding configuration
    exchange: Optional[Exchange] = None
    routing_key: Optional[str] = None
    arguments: Optional[dict] = None


class RabbitMQConfig(BaseModel):
    """Configuration for a RabbitMQ service instance"""

    vhost: str = "/"
    exchanges: list[Exchange]
    queues: list[Queue]


class RabbitMQBase(ABC):
    """Base class for RabbitMQ connections with shared configuration"""

    def __init__(self, config: RabbitMQConfig):
        settings = Settings()
        self.host = settings.config.rabbitmq_host
        self.port = settings.config.rabbitmq_port
        self.username = settings.secrets.rabbitmq_default_user
        self.password = settings.secrets.rabbitmq_default_pass
        self.config = config

        self._connection = None
        self._channel = None

    @property
    def is_connected(self) -> bool:
        """Check if we have a valid connection"""
        return bool(self._connection)

    @property
    def is_ready(self) -> bool:
        """Check if we have a valid channel"""
        return bool(self.is_connected and self._channel)

    @abstractmethod
    def connect(self) -> None | Awaitable[None]:
        """Establish connection to RabbitMQ"""
        pass

    @abstractmethod
    def disconnect(self) -> None | Awaitable[None]:
        """Close connection to RabbitMQ"""
        pass

    @abstractmethod
    def declare_infrastructure(self) -> None | Awaitable[None]:
        """Declare exchanges and queues for this service"""
        pass


class SyncRabbitMQ(RabbitMQBase):
    """Synchronous RabbitMQ client"""

    @property
    def is_connected(self) -> bool:
        return bool(self._connection and self._connection.is_open)

    @property
    def is_ready(self) -> bool:
        return bool(self.is_connected and self._channel and self._channel.is_open)

    @conn_retry("RabbitMQ", "Acquiring connection")
    def connect(self) -> None:
        if self.is_connected:
            return

        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.config.vhost,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )

        self._connection = pika.BlockingConnection(parameters)
        self._channel = self._connection.channel()
        self._channel.basic_qos(prefetch_count=1)

        self.declare_infrastructure()

    def disconnect(self) -> None:
        if self._channel:
            if self._channel.is_open:
                self._channel.close()
            self._channel = None
        if self._connection:
            if self._connection.is_open:
                self._connection.close()
            self._connection = None

    def declare_infrastructure(self) -> None:
        """Declare exchanges and queues for this service"""
        if not self.is_ready:
            self.connect()

        if self._channel is None:
            raise RuntimeError("Channel should be established after connect")

        # Declare exchanges
        for exchange in self.config.exchanges:
            self._channel.exchange_declare(
                exchange=exchange.name,
                exchange_type=exchange.type.value,
                durable=exchange.durable,
                auto_delete=exchange.auto_delete,
            )

        # Declare queues and bind them to exchanges
        for queue in self.config.queues:
            self._channel.queue_declare(
                queue=queue.name,
                durable=queue.durable,
                auto_delete=queue.auto_delete,
                arguments=queue.arguments,
            )
            if queue.exchange:
                self._channel.queue_bind(
                    queue=queue.name,
                    exchange=queue.exchange.name,
                    routing_key=queue.routing_key or queue.name,
                )

    def publish_message(
        self,
        routing_key: str,
        message: str,
        exchange: Optional[Exchange] = None,
        properties: Optional[BasicProperties] = None,
        mandatory: bool = True,
    ) -> None:
        if not self.is_ready:
            self.connect()

        if self._channel is None:
            raise RuntimeError("Channel should be established after connect")

        self._channel.basic_publish(
            exchange=exchange.name if exchange else "",
            routing_key=routing_key,
            body=message.encode(),
            properties=properties or BasicProperties(delivery_mode=2),
            mandatory=mandatory,
        )

    def get_channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        if not self.is_ready:
            self.connect()
        if self._channel is None:
            raise RuntimeError("Channel should be established after connect")
        return self._channel


class AsyncRabbitMQ(RabbitMQBase):
    """Asynchronous RabbitMQ client"""

    @property
    def is_connected(self) -> bool:
        return bool(self._connection and not self._connection.is_closed)

    @property
    def is_ready(self) -> bool:
        return bool(self.is_connected and self._channel and not self._channel.is_closed)

    @conn_retry("AsyncRabbitMQ", "Acquiring async connection")
    async def connect(self):
        if self.is_connected:
            return

        self._connection = await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            login=self.username,
            password=self.password,
            virtualhost=self.config.vhost.lstrip("/"),
        )
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=1)

        await self.declare_infrastructure()

    async def disconnect(self):
        if self._channel:
            await self._channel.close()
            self._channel = None
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def declare_infrastructure(self):
        """Declare exchanges and queues for this service"""
        if not self.is_ready:
            await self.connect()

        if self._channel is None:
            raise RuntimeError("Channel should be established after connect")

        # Declare exchanges
        for exchange in self.config.exchanges:
            await self._channel.declare_exchange(
                name=exchange.name,
                type=exchange.type.value,
                durable=exchange.durable,
                auto_delete=exchange.auto_delete,
            )

        # Declare queues and bind them to exchanges
        for queue in self.config.queues:
            queue_obj = await self._channel.declare_queue(
                name=queue.name,
                durable=queue.durable,
                auto_delete=queue.auto_delete,
                arguments=queue.arguments,
            )
            if queue.exchange:
                exchange = await self._channel.get_exchange(queue.exchange.name)
                await queue_obj.bind(
                    exchange, routing_key=queue.routing_key or queue.name
                )

    async def publish_message(
        self,
        routing_key: str,
        message: str,
        exchange: Optional[Exchange] = None,
        persistent: bool = True,
    ) -> None:
        if not self.is_ready:
            await self.connect()

        if self._channel is None:
            raise RuntimeError("Channel should be established after connect")

        if exchange:
            exchange_obj = await self._channel.get_exchange(exchange.name)
        else:
            exchange_obj = self._channel.default_exchange

        await exchange_obj.publish(
            aio_pika.Message(
                body=message.encode(),
                delivery_mode=(
                    aio_pika.DeliveryMode.PERSISTENT
                    if persistent
                    else aio_pika.DeliveryMode.NOT_PERSISTENT
                ),
            ),
            routing_key=routing_key,
        )

    async def get_channel(self) -> aio_pika.abc.AbstractChannel:
        if not self.is_ready:
            await self.connect()
        if self._channel is None:
            raise RuntimeError("Channel should be established after connect")
        return self._channel
