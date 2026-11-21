from sqlalchemy import BigInteger, Integer
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import DeclarativeBase

# SQLite only auto-increments INTEGER primary keys. Keep BIGINT in MySQL while
# testing the same models against SQLite in the automated test suite.
BigInt = BigInteger().with_variant(Integer, "sqlite")

# The checked-in order seed uses BIGINT UNSIGNED for order/order-item ids.
# Any foreign key that references those tables must use the exact same type in
# MySQL, otherwise InnoDB raises error 3780 (incompatible FK columns).
UnsignedBigInt = (
    BigInteger()
    .with_variant(mysql.BIGINT(unsigned=True), "mysql")
    .with_variant(Integer, "sqlite")
)


class Base(DeclarativeBase):
    pass


# Kept here so Alembic or a future migration tool can import all metadata.
def load_models() -> None:
    from app.models import (  # noqa: F401
        AuthSession,
        Conversation,
        ConversationMessage,
        Merchant,
        Order,
        OrderItem,
        Ticket,
        TicketAgentRun,
        User,
    )
